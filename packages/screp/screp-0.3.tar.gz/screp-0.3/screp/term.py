from .actiondir import make_action

class Term(object):
    def __init__(self, actions=None):
        if actions is None:
            actions = []

        self._actions = []

        for a in actions:
            self.add_action(a)


    def add_action(self, action):
        if len(self._actions) > 0:
            if not action.can_follow(self.last_action):
                raise TypeError('%s cannot follow %s: expects type %s, receives %s!'\
                        % (action, self.last_action, action.in_type, self.last_action.out_type))
        self._actions.append(action)


    @property
    def last_action(self):
        return self._actions[-1]


    def execute(self, value):
        if len(self._actions) == 0:
            raise ValueError("No actions defined!")

        for a in self._actions:
            value = a.execute(value)

        return value


    @property
    def out_type(self):
        if len(self._actions) == 0:
            return None
        else:
            return self.last_action.out_type


def make_term(pterm, anchors_factory, required_out_type=None):
    actions = [anchors_factory.make_anchor_action(pterm.anchor.name, pterm.anchor.identification)] + map(lambda ta: make_action(ta), pterm.accessors + pterm.filters)
    if required_out_type is not None:
        if len(actions) == 0 or actions[-1].out_type != required_out_type:
            raise ValueError("Term must have out_type '%s', has '%s'!" % (required_out_type, actions[-1].out_type))
    return Term(actions)


