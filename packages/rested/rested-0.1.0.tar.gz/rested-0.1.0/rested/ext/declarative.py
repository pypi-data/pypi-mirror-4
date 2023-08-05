from ..metadata import Metadata
from ..entity import Entity

from ..action import Action
from ..field import Field
from ..relation import Relation

ACCEPTED_ARGUMENTS = [
    Action,
    Field,
    Relation
]

class BaseMetaClass(type):
    def __new__(cls, type_name, subclasses, type_dict):
        add_metadata = False

        if subclasses == (object,) or subclasses == (BaseClass,):
            add_metadata = False
        else:
            add_metadata = True

        new_type = type.__new__(cls, type_name, subclasses, type_dict)

        if add_metadata:
            entity_arguments = list()

            for name, instance in type_dict.items():
                for accepted_type in ACCEPTED_ARGUMENTS:
                    if isinstance(instance, accepted_type):
                        if instance.name is None:
                            instance.name = name
                        entity_arguments.append(instance)

            if new_type.__entity_name__ is None:
                new_type.__entity_name__ = type_name

            entity = Entity(
                new_type.__entity_name__,
                *entity_arguments,
                **new_type.__entity_args__)

            new_type.m.add_entity(entity, extra=new_type)

        return new_type

class BaseClass(object):
    __metaclass__ = BaseMetaClass
    __entity_name__ = None
    __entity_args__ = dict()

    @classmethod
    def resolve(cls):
        return cls.m.resolve_entity(cls.__entity_name__)

def declarative_base(name="Base"):
    return type(
        name,
        (BaseClass,),
        {
            "m": Metadata(),
        })
