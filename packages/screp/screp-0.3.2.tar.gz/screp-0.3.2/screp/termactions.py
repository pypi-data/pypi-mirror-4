import lxml
from lxml.etree import (
        XPath,
        )
from lxml.cssselect import CSSSelector
import re

from .utils import (
        raise_again,
        generic_translator,
        preprocess_selector,
        )


class BaseTermAction(object):
    in_type = None
    out_type = None

    @staticmethod
    def _check_types_match(t1, t2):
        return (t1 is None) or (t2 is None) or (t1 == t2)


    def can_precede(self, other):
        return BaseTermAction._check_types_match(self.out_type, other.in_type)


    def can_follow(self, other):
        return BaseTermAction._check_types_match(self.in_type, other.out_type)


    def execute(self, value):
        pass


class GenericTermAction(BaseTermAction):
    def __init__(self, f, in_type=None, out_type=None, args=None, identification=None):
        self._f = f
        self._id = identification
        self.in_type = in_type
        self.out_type = out_type
        if args is None:
            args = []
        self._args = list(args)


    def sub_execute(self, value):
        return self._f(value, *self._args)


    def execute(self, value):
        try:
            return self.sub_execute(value)
        except Exception as e:
            raise_again('%s: %s' % (self._id, e))


class GenericSelectorTermAction(GenericTermAction):
    def __init__(self, f, selector, in_type=None, out_type=None, identification=None, args=None):
        super(GenericSelectorTermAction, self).__init__(f, in_type=in_type, out_type=out_type, identification=identification, args=args)

        self._selector = selector


    def sub_execute(self, value):
        return self._f(value, self._selector, *self._args)


class AnchorTermAction(BaseTermAction):
    in_type = 'context'
    # out_type is set at instantiation, since it can vary

    def __init__(self, anchor, out_type, identification=None):
        self._anchor = anchor
        self._id = identification
        self.out_type = out_type


    def execute(self, context):
        # value must be a context
        return context.get_anchor(self._anchor)


class RegexTermAction(BaseTermAction):
    in_type = 'string'
    out_type = 'string'

    char_to_flag = {
            'i': re.IGNORECASE,
            'l': re.LOCALE,
            'm': re.MULTILINE,
            's': re.DOTALL,
            'u': re.UNICODE,
            }

    allowed_flags = frozenset(char_to_flag.keys() + ['g', 'f'])

    def __init__(self, args, identification=None):
        self._id = identification

        if len(args) < 2 or len(args) > 3:
            raise ValueError("Invalid number of arguments for 'resub'!")

        self._replace = args[1]

        if len(args) == 3:
            sflags = args[2]
        else:
            sflags = ''

        (self._count, flags) = self._handle_flags(sflags)

        self._re = re.compile(args[0], flags=flags)


    def _handle_flags(self, flags):
        flags = set(flags)

        bflags = 0

        if not flags <= self.allowed_flags:
            raise ValueError("Unknown flags: '%s'!" % (''.join(list(flags - self.allowed_flags)),))

        for (k, f) in self.char_to_flag.items():
            if k in flags:
                bflags |= f

        if 'g' in flags and 'f' in flags:
            raise ValueError("Only one of 'g' and 'f' is allowed!")

        count = 0

        if 'f' in flags:
            count = 1

        return (count, bflags)


    def execute(self, value):
        return self._re.sub(self._replace, value, count=self._count)


def make_action_of_class(cls, f, in_type, out_type):
    def builder(identification, args):
        return cls(f, in_type=in_type, out_type=out_type, identification=identification, args=args)

    return builder


def make_generic_action(f, in_type, out_type):
    return make_action_of_class(GenericTermAction, f, in_type, out_type)


def make_custom_selector_action(f, selector_ctor, in_type, out_type):
    def builder(identification, args):
        selector = selector_ctor(preprocess_selector(args[0]))
        args = args[1:]
        return GenericSelectorTermAction(f, selector, in_type=in_type, out_type=out_type, identification=identification, args=args)

    return builder


def make_selector_action(f, in_type, out_type):
    return make_custom_selector_action(f, CSSSelector, in_type, out_type)


def make_axis_selector_action(f, axis, in_type, out_type):
    return make_custom_selector_action(f, lambda spec: XPath(generic_translator.css_to_xpath(spec, prefix=axis)), in_type, out_type)
