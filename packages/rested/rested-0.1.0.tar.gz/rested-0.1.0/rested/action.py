from rested.argument import Argument
from rested.field import Field

ACTION_METHODS = ["read", "write", "update", "delete"]
ACTION_TYPES = ["single", "collection", "empty"]

__all__ = ["Action"]


class Action(object):
    """
    Defines an action against an entity.
    """
    def __init__(self, *args, **kw):
        self.name = None
        self.help = kw.pop("help", "(missing help)")
        self.inherit_fields = kw.pop("inherit_fields", False)
        self.method = kw.pop("method", "read").lower()
        self.action_type = kw.pop("action_type", "single")

        if self.method not in ACTION_METHODS:
            raise ValueError("Invalid method: {0}".format(
                self.method))

        if self.action_type not in ACTION_TYPES:
            raise ValueError("Invalid action type: {0}".format(
                self.action_type))

        self.fields = list()
        self.arguments = list()

        for arg in args:
            if isinstance(arg, basestring):
                self.name = arg
            elif isinstance(arg, Argument):
                self.arguments.append(arg)
            elif isinstance(arg, Field):
                self.fields.append(arg)
            else:
                raise TypeError(arg)
