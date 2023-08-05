from rested.types import String
from rested.types import FieldType


class Field(object):
    def __init__(self, *args, **kw):
        self.name = None
        self.field_type = String
        self.required = kw.pop("required", True)
        self.default = kw.pop("default", None)

        self.help = kw.pop("help", "(missing help)")

        for arg in args:
            if isinstance(arg, basestring):
                self.name = arg
            elif isinstance(arg, FieldType):
                self.field_type = arg
            elif isinstance(arg, type) and issubclass(arg, FieldType):
                self.field_type = arg
            else:
                raise TypeError(arg)

        if issubclass(self.field_type, FieldType):
            self.field_type = self.field_type()

        if not isinstance(self.field_type, FieldType):
            raise TypeError(self.field_type)
