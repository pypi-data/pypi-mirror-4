from .field import Field
from .action import Action
from .relation import Relation

class Entity(object):
    def __init__(self, name, *definitions, **kw):
        self.name = name

        self.fields = list()
        self.actions = list()
        self.relations = list()

        self.help = kw.pop("help", "(missing help)")
        self.plural = kw.pop("plural", name.lower())
        self.singular = kw.pop("singular", name.lower())

        for d in definitions:
            if isinstance(d, Field):
                self.fields.append(d)
            elif isinstance(d, Action):
                self.actions.append(d)
            elif isinstance(d, Relation):
                self.relations.append(d)
            else:
                raise TypeError(d)

    def check(self):
        for field in self.fields:
            if not field.name:
                raise ValueError(
                    "Invalid or missing name for field {0}".format(field))

        for action in self.actions:
            if not action.name:
                raise ValueError(
                    "Invalid or missing name for action {0}".format(action))

        for relation in self.relations:
            if not relation.name:
                raise ValueError(
                    "Invalid or missing name for relation {0}".format(relation))

    def __repr__(self):
        return "Entity(name={0})".format(self.name)
