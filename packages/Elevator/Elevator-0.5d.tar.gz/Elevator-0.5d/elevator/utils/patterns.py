from collections import Sequence

# Enums beautiful python implementation
# Used like this :
# Numbers = enum('ZERO', 'ONE', 'TWO')
# >>> Numbers.ZERO
# 0
# >>> Numbers.ONE
# 1
# Found here: http://stackoverflow.com/questions/36932/whats-the-best-way-to-implement-an-enum-in-python
def enum(*sequential, **named):
    enums = dict(zip(sequential, range(len(sequential))), **named)
    return type('Enum', (), enums)


class Singleton(type):
    def __init__(cls, name, bases, dict):
        super(Singleton, cls).__init__(name, bases, dict)
        cls.instance = None

    def __call__(cls, *args, **kw):
        if cls.instance is None:
            cls.instance = super(Singleton, cls).__call__(*args, **kw)
        return cls.instance

    def __del__(cls, *args, **kw):
        cls.instance is None


class DestructurationError(Exception):
    pass


def destructurate(container):
    try:
        return container[0], container[1:]
    except (KeyError, AttributeError):
        raise DestructurationError("Can't destructurate a non-sequence container")
