from pyparsing import (
        Word,
        Optional,
        Literal,
        Keyword,
        Forward,
        NoMatch,
        ZeroOrMore,
        QuotedString,
        Group,
        Combine,
        nestedExpr,
        ungroup,
        )

from .idloc import (
        LocationFactory,
        Identification,
        )

location_factory = LocationFactory('Unknown')


def make_location(index):
    return location_factory.make_location(index)


class location_factory_context(object):
    def __init__(self, loc_fac):
        self.loc_fac = loc_fac

    
    def __enter__(self):
        global location_factory
        self.old_loc_fac = location_factory
        location_factory = self.loc_fac


    def __exit__(self, t, v, tb):
        global location_factory
        location_factory = self.old_loc_fac


def set_parser_results(res, value):
    res[0] = value

    del res[1:]

    return res


def set_action_type(action, type):
    action.identification.type = type


def any_of_keywords(kws):
    t = NoMatch()

    for k in kws:
        t = t ^ Keyword(k)

    return t

anchor_kws = ['$', '@']

class ParsedTerm(object):
    def __init__(self, anchor, accessors, filters):
        self.anchor = anchor
        self.accessors = accessors
        self.filters = filters


class ParsedTermAction(object):
    def __init__(self, name, identification, args=None):
        self.name = name
        if args is None:
            args = ()

        self.args = args

        self.identification = identification


    def __str__(self):
        return "ParsedTermAction<%s>" % (self.identification,)


    __repr__ = __str__


class ParsedAnchor(object):
    def __init__(self, name, identification=None):
        self.name = name
        self.identification = identification


    def __str__(self):
        return "ParsedAnchor<%s>" % (self.identification,)


    __repr__ = __str__


digits = '0123456789'
uppers = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
lowers = uppers.lower()
underscore = '_'

identifier_parser = Combine(Word(uppers + lowers + underscore, exact=1) + Optional(Word(uppers + lowers + digits + underscore), default=''))

integer_parser = (Optional('-', default='') + Word(digits)).setParseAction(lambda s, l, t: set_parser_results(t, t[0] + t[1]))

quoted_string_parser = QuotedString(quoteChar='\'', escChar='\\', escQuote='\\\'') ^\
        QuotedString(quoteChar='\"', escChar='\\', escQuote='\\\"')


argument_parser = identifier_parser ^ integer_parser ^ quoted_string_parser

argument_list_parser = Literal('(').suppress() + argument_parser + ZeroOrMore(Literal(',').suppress() + argument_parser) + Literal(')').suppress()

action_parser = identifier_parser + Optional(Group(argument_list_parser), default=[])

action_parser.setParseAction(lambda s, l, t: set_parser_results(t, 
    ParsedTermAction(t[0], Identification(t[0], 'action', make_location(l)), args=t[1])))

filter_parser = Literal('|').suppress() + action_parser

filter_parser.setParseAction(lambda s, l, t: set_action_type(t[0], 'filter'))

accessor_parser = Literal('.').suppress() + action_parser

accessor_parser.setParseAction(lambda s, l, t: set_action_type(t[0], 'accessor'))

anchor_parser = (any_of_keywords(anchor_kws) ^ identifier_parser)

anchor_parser.addParseAction(lambda s, l, t: set_parser_results(t,
    ParsedAnchor(t[0], Identification(t[0], 'anchor', make_location(l)))))

term_parser = anchor_parser + Group(ZeroOrMore(accessor_parser)) + Group(ZeroOrMore(filter_parser))

term_parser.setParseAction(lambda s, l, t: set_parser_results(t, ParsedTerm(t[0], tuple(t[1]), tuple(t[2]))))

curly_term_parser = ungroup(nestedExpr('{', '}', content=term_parser))


def parse_term(string):
    return term_parser.parseString(string, parseAll=True)[0]


if __name__ == '__main__':
    import sys

    for _ in  action_parser.scanString(sys.argv[1], maxMatches=1):
        print _


