from pyparsing import (
        Literal,
        ZeroOrMore,
        StringEnd,
        Group,
        SkipTo,
        )
import re

from .term_parser import (
        term_parser,
        curly_term_parser,
        parse_term,
        location_factory_context,
        identifier_parser,
        )
from .term import make_term
from .anchor import make_anchor
from .idloc import (
        LocationFactory,
        )
from .formatter import (
        CSVFormatter,
        JSONFormatter,
        GeneralFormatter,
        )
from .utils import raise_again

comma = Literal(',').suppress()

equal = Literal('=').suppress()

csv_format_parser = term_parser + ZeroOrMore(comma + term_parser) + StringEnd()

json_assignement_parser = Group(identifier_parser + equal + term_parser)

json_format_parser = json_assignement_parser + ZeroOrMore(comma + json_assignement_parser) + StringEnd()

general_format_parser = ZeroOrMore(SkipTo(curly_term_parser).leaveWhitespace() + curly_term_parser) + SkipTo(StringEnd()).leaveWhitespace() + StringEnd()


def parse_csv_formatter(value, anchors_factory, header=None):
    with location_factory_context(LocationFactory('csv_format')):
        result = csv_format_parser.parseString(value)

        terms = map(lambda pterm: make_term(pterm, anchors_factory, required_out_type='string'), result)

        return (CSVFormatter(len(terms), header=header), terms)


def parse_json_formatter(value, anchors_factory, **kwoptions):
    with location_factory_context(LocationFactory('json_format')):
        result = json_format_parser.parseString(value)

        keys = [x[0] for x in result]

        terms = map(lambda pterm: make_term(pterm, anchors_factory, required_out_type='string'), [x[1] for x in result])

        return (JSONFormatter(keys, **kwoptions), terms)


def parse_general_formatter(value, anchors_factory, escaped):
    with location_factory_context(LocationFactory('general_format')):
        result = list(general_format_parser.parseString(value))

        terms = map(lambda pterm: make_term(pterm, anchors_factory, required_out_type='string'), result[1::2])

        if escaped:
            inter_strings = map(lambda x: x.decode('string_escape'), result[0::2])
        else:
            inter_strings = result[0::2]

        return (GeneralFormatter(inter_strings), terms)


anchor_re = re.compile('^(?P<name>[_A-Za-z][_A-Za-z0-9]*)\s*=(?P<term_spec>.*)$')


def parse_anchor(string, anchors_factory):
    m = anchor_re.match(string)
    if m is None:
        raise ValueError('Invalid anchor format')

    name = m.group('name')

    try:
        with location_factory_context(LocationFactory('anchor[%s]' % (name,), index_offset=m.start('term_spec'))):
            pterm = parse_term(m.group('term_spec'))
    except Exception as e:
        raise_again("Anchor '%s': %s" % (name, e))

    return make_anchor(name, pterm, anchors_factory)


if __name__ == '__main__':
    import sys

    print parse_csv_formatter(sys.argv[1])
