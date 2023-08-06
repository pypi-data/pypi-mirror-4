from base import Dictifier, Invalid
from dictifiable import Dictifiable

class UnknownType(Exception):
    '''Raised when a Polymorph encounters an unknown type.'''
    pass

class Polymorph(Dictifier):
    '''A dictifier that selects between several dictifiables based on classes.

    The mapping argument is a dict whose keys are strings and whose values are
    either (class_list, Dictifier) pairs or Dictifiable classes.

    Polymorph can Dictify any object that is an instance of one of the
    Dictifiable classes or any class in one of the class_list entries; it will
    dictify it as a tuple of (name, value), where name identifies which
    Dictifier was used and value is the dictified object; on undictifiance, it
    undictifies the value using the Dictifier for that name.

    For example:

    >>> from basic import Number, Complex
    >>> from schema import SchemaObj
    >>> class Point(SchemaObj):
    ...     field_types = dict(x=Number(), y=Complex())
    ...
    >>> num_or_point = Polymorph({'point':Point, 'num':((int, float), Number())})
    >>> num_or_point.dictify(12)
    ('num', 12)
    >>> num_or_point.dictify(3.5)
    ('num', 3.5)
    >>> num_or_point.dictify(Point(x=1, y=3)) == ('point', {'x':1, 'y':3})
    True
    >>> num_or_point.undictify(('num', 42))
    42.0
    >>> p = num_or_point.undictify(('point', {'x':-1, 'y':'2+2j'}))
    >>> p.x
    -1.0
    >>> p.y
    (2+2j)

    It will validate only the types in its list:

    >>> num_or_point.validate(3)
    >>> num_or_point.validate(3.5)
    >>> num_or_point.validate(p)
    >>> num_or_point.validate('hi')
    Traceback (most recent call last):
    ...
    Invalid: type_error
    '''
    def __init__(self, mapping):
        super(Polymorph, self).__init__()
        self.mapping = {}
        self.reverse_mapping = {}
        for name, data in mapping.items():
            if isinstance(data, type) and issubclass(data, Dictifiable):
                classes, dfier = (data,), data.dfier()
            else:
                classes, dfier = data
            self.mapping[name] = dfier
            for cls in classes:
                self.reverse_mapping[cls] = (name, dfier)

    def get_dfier(self, value):
        '''Given an object, get the corresponding name and dictifier.'''
        for basetype in type(value).__mro__:
            if basetype in self.reverse_mapping:
                return self.reverse_mapping[basetype]
        raise UnknownType(type(value).__name__)

    def undictify(self, value, **kwargs):
        '''Convert a dictified value to an object and return it.'''
        if not isinstance(value, (list, tuple)):
            raise Invalid('type_error')
        if len(value) != 2:
            raise Invalid('bad_list')
        name, value = value
        return self.mapping[name].undictify(value, **kwargs)

    def dictify(self, value, **kwargs):
        name, dfier = self.get_dfier(value)
        return (name, dfier.dictify(value, **kwargs))

    def validate(self, value, **kwargs):
        try:
            name, dfier = self.get_dfier(value)
        except UnknownType:
            raise Invalid("type_error")
        dfier.validate(value, **kwargs)

if __name__ == '__main__':
    import doctest
    doctest.testmod()
