from base import Dictifier, Invalid

class _EmptyClass:
    '''Placeholder class for undictifying Dictifiable instances.'''
    pass


class _EmptyNSClass(object):
    '''Placeholder class for undictifying Dictifiable instances.'''
    pass


def empty_instance(cls):
    '''Create an instance of cls without invoking cls.__init__'''
    if issubclass(cls, object):
        instance = _EmptyNSClass()
    else:
        instance = _EmptyClass()
    instance.__class__ = cls
    return instance


class DictifiableDictifier(Dictifier):
    '''Dictifier for Dictifiables.

    In general users will not create instances of this class directly, but will
    instead use the classmethod Dictifiable.dfier(), which returns an instance
    of this class for that Dictifiable type.
    '''
    def __init__(self, dictifiable_cls):
        self.cls = dictifiable_cls

    def dictify(self, value, **kwargs):
        return value.__dictify__(**kwargs)

    def undictify(self, value, **kwargs):
        instance = empty_instance(self.cls)
        instance.__undictify__(value, **kwargs)
        return instance

    def validate(self, value, **kwargs):
        if not isinstance(value, self.cls):
            raise Invalid("type_error", expected=self.cls.__name__)
        value.__validate__(**kwargs)


class Dictifiable(object):
    '''An object that knows how to dictify/undictify itself.

    The class should implement three functions:

    __dictify__(self, **kwargs): dictify self
    __undictify__(self, value, **kwargs): undictify self from value
    __validate__(self, **kwargs): validate self

    __dictify__ and __validate__ are straightforward; __undictify__ will be
    called on a blank instance of the class (i.e., without calling __init__), so
    it must set up the new instance from scratch.

    The classmethod .dfier() returns a Dictifier for this class.

    Dictifiable classes also expose three helper methods:

    self.dictify(**kwargs) - same as cls.dfier().dictify(self, **kwargs)
    cls.undictify(val, **kwargs) - same as cls.dfier().undictify(val, **kwargs)
    self.validate(**kwargs) - same as cls.dfier().validate(self, **kwargs)

    Note that as a consequence, the class itself very nearly adheres to the
    dictify protocol, since the instance methods dictify and validate can be
    called as classmethods and passed instances as arguments. However,
    cls.validate will break if the value is not an instance of the class,
    because python doesn't allow classmethods to be called on non-instances.

    Thus, you should use cls.dfier() if you need the dictifier for this class,
    instead of just using the class.

    '''
    # This class is almost itself a dictifier, but it isn't quite, because the
    # class's validate functions will crash given a value that isn't an instance
    # Python 3 will fix this, because instance methods are callable as
    # classmethods with any argument for self
    @classmethod
    def dfier(cls):
        return DictifiableDictifier(cls)

    def __dictify__(self, **kwargs):
        raise NotImplementedError()

    def __undictify__(self, value, **kwargs):
        raise NotImplementedError

    def __validate__(self, **kwargs):
        pass

    def dictify(self, **kwargs):
        return self.dfier().dictify(self, **kwargs)

    @classmethod
    def undictify(cls, value, **kwargs):
        return cls.dfier().undictify(value, **kwargs)

    def validate(self, **kwargs):
        return self.dfier().validate(self, **kwargs)


if __name__ == '__main__':
    import doctest
    doctest.testmod()
