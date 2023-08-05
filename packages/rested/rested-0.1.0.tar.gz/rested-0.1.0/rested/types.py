class FieldType(object):
    """
    Base class for types.

    Custom types can be created by inheriting from this and
    defining the __call__ function with one string parameter.

    Whatever gets returned should be associated to the finalized namespace.

    metavar: The name of the (meta)argument on fields, like 'bar' in '--foo bar'.
    """
    metavar = None

    def __init__(self, **kw):
        self.metavar = kw.pop("metavar", self.metavar)

    def __repr__(self):
        return self.__class__.__name__

class String(FieldType):
    metavar = "string"

    def __call__(self, value):
        return str(value)

class Integer(FieldType):
    metavar = "number"

    def __call__(self, value):
        return int(value)
