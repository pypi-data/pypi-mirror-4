__all__ = [
    "OneToMany",
    "ManyToMany",
    "OneToOne",
    "has_many",
    "with_many",
    "has_one",
]


class Relation(object):
    metadesc = None

    def __init__(self, *args, **kw):
        if len(args) == 2:
            self.name = args[0]
            self.ref = args[1]
        elif len(args) == 1:
            self.name = None
            self.ref = args[0]
        else:
            raise RuntimeError(
                "Invalid argument length, expected (ref) or (name, ref)")

        self.help = kw.pop(
            "help",
            "missing help for '{0}'".format(self.metadesc))

    def __repr__(self):
        return "Relation[{0}](ref={self.ref})".format(
            self.metadesc, self=self)


class OneToMany(Relation):
    metadesc = "one-to-many (1:n)"


class ManyToMany(Relation):
    metadesc = "many-to-many (n:n)"


class OneToOne(Relation):
    metadesc = "one-to-one (1:1)"


def has_many(*args, **kw):
    """
    Declarte that an entity has many associated entities.
    """
    return OneToMany(*args, **kw)


def with_many(*args, **kw):
    return ManyToMany(*args, **kw)


def has_one(*args, **kw):
    return OneToOne(*args, **kw)
