import screp.term as term_module


class Anchor(object):
    def __init__(self, name, term):
        self.name = name
        self.term = term


    def execute(self, context):
        return self.term.execute(context)


    @property
    def out_type(self):
        return self.term.out_type


def make_anchor(name, pterm, anchors_factory):
    term = term_module.make_term(pterm, anchors_factory)

    return Anchor(name, term)
