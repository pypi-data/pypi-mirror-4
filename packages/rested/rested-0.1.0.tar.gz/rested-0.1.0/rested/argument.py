class Argument(object):
    """
    Defines an argument against an entity.
    """
    def __init__(self, name, **kw):
        self.name = name
        self.help = kw.pop("help", "(missing help)")
