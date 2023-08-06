from .termactions import  AnchorTermAction
from .term import Term
from .anchor import Anchor


def make_id_anchor(name, out_type):
    return Anchor(name, Term([AnchorTermAction(name, out_type)]))


class AnchorContext(object):
    def __init__(self, anchors):
        self._anchors = dict(anchors)


    def get_anchor(self, name):
        return self._anchors[name]


    def add_anchor(self, name, value):
        self._anchors[name] = value


class AnchorContextFactory(object):
    def __init__(self, primary_anchors):
        self._anchors = map(lambda x: make_id_anchor(*x), primary_anchors)


    def get_anchor(self, name):
        # return the last definition of that anchor
        return [x for x in self._anchors if x.name == name][-1]


    def add_anchor(self, anchor):
        self._anchors.append(anchor)


    def make_context(self, primary_anchors_values):
        context = AnchorContext(primary_anchors_values)

        for anchor in self._anchors:
            context.add_anchor(anchor.name, anchor.execute(context))

        return context


    def make_anchor_action(self, name, identification):
        return AnchorTermAction(name, self.get_anchor(name).out_type, identification=identification)
