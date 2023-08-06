from lxml.etree import (
        XPath,
        tostring,
        )

from .termactions import (
        make_generic_action,
        make_selector_action,
        make_axis_selector_action,
        make_custom_selector_action,
        RegexTermAction,
        )
from .utils import (
        generic_translator,
        preprocess_selector,
        )


def match_selector(elset, selector):
    return sum(map(selector, elset), [])


def get_attr(element, attr):
    v = element.get(attr)
    if v is None:
        raise Exception("Element doesn't have attribute '%s'!" % (attr,))
    else:
        return v


def get_parent(element):
    parent = element.getparent()

    if parent is None:
        raise ValueError("Could not get parent: element is root!")
    else:
        return parent


def regex_action_builder(identification, args):
    return RegexTermAction(args, identification=identification)


class SiblingSelector(object):
    def __init__(self, selector):
        self._preceding_sel = XPath(generic_translator.css_to_xpath(preprocess_selector(selector), prefix="preceding-sibling::"))
        self._following_sel = XPath(generic_translator.css_to_xpath(preprocess_selector(selector), prefix="following-sibling::"))


    def __call__(self, element):
        return self._preceding_sel(element) + self._following_sel(element)


actions = [
        # accessors
        (('first', 'f'),            make_generic_action(lambda s: s[0], 'element_set', 'element')),
        (('last', 'l'),             make_generic_action(lambda s: s[-1], 'element_set', 'element')),
        (('class',),                make_generic_action(lambda e: get_attr(e, 'class'), 'element', 'string')),
        (('id',),                   make_generic_action(lambda e: get_attr(e, 'id'), 'element', 'string')),
        (('parent', 'p'),           make_generic_action(lambda e: get_parent(e), 'element', 'element')),
        (('text',),                 make_generic_action(lambda e: e.text, 'element', 'string')),
        (('tag',),                  make_generic_action(lambda e: e.tag, 'element', 'string')),
        (('attr', 'a'),             make_generic_action(lambda e, a: get_attr(e, a), 'element', 'string')),
        (('nth', 'n'),              make_generic_action(lambda s, i: s[int(i)], 'element_set', 'element')),
        (('desc', 'd'),             make_selector_action(lambda e, sel: sel(e), 'element', 'element_set')),
        (('fdesc', 'fd'),           make_selector_action(lambda e, sel: sel(e)[0], 'element', 'element')),
        (('ancestors', 'ancs'),     make_axis_selector_action(lambda e, sel: sel(e), 'ancestor::', 'element', 'element_set')),
        (('children', 'kids'),      make_axis_selector_action(lambda e, sel: sel(e), 'child::', 'element', 'element_set')),
        (('fsiblings', 'fsibs'),    make_axis_selector_action(lambda e, sel: sel(e), 'following-sibling::', 'element', 'element_set')),
        (('psiblings', 'psibs'),    make_axis_selector_action(lambda e, sel: sel(e), 'preceding-sibling::', 'element', 'element_set')),
        (('siblings', 'sibs'),      make_custom_selector_action(lambda e, sel: sel(e), SiblingSelector, 'element', 'element_set')),
        (('matching', 'm'),         make_axis_selector_action(match_selector, 'self::', 'element_set', 'element_set')),
        (('tostring', 'string'),    make_generic_action(lambda e: tostring(e), 'element', 'string')),


        # functions/filters
        (('upper',),                make_generic_action(lambda s: s.upper(), 'string', 'string')),
        (('lower',),                make_generic_action(lambda s: s.lower(), 'string', 'string')),
        (('trim', 't'),             make_generic_action(lambda s: s.strip(), 'string', 'string')),
        (('strip',),                make_generic_action(lambda s, chars: s.strip(chars), 'string', 'string')),
        (('replace',),              make_generic_action(lambda s, old, new: s.replace(old, new), 'string', 'string')),
        (('resub',),                regex_action_builder),
        ]


def multiply_keys(lst):
    for keys, val in lst:
        for k in keys:
            yield (k, val)


actions_dir = dict(multiply_keys(actions))


def make_action(parsed_action):
    try:
        return actions_dir[parsed_action.name](parsed_action.identification, parsed_action.args)
    except KeyError:
        raise Exception("Unknown action '%s'!" % (parsed_action.identification,))


