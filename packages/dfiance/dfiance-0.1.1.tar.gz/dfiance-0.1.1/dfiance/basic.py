import numbers

from base import Dictifier, Invalid

class TypeDictifier(Dictifier):
    '''Dictifier for simple types, such as integers and strings.

    Dfiance is a no-op:

    >>> intdfy = TypeDictifier(int)
    >>> intdfy.dictify(4)
    4

    Undfiance calls self.type:

    >>> intdfy.undictify(4)
    4
    >>> intdfy.undictify("4")
    4
    >>> intdfy.undictify("hello")
    Traceback (most recent call last):
    ...
    Invalid: type_error

    Validation uses isinstance:

    >>> intdfy.validate(3)
    >>> intdfy.validate(3.5)
    Traceback (most recent call last):
    ...
    Invalid: type_error
    '''
    type = None
    error_msg = 'type_error'
    allowed_types = None

    def __init__(self, type=None, error_msg=None, allowed_types=None):
        if type:
            self.type = type
        if error_msg:
            self.error_msg = error_msg
        if allowed_types:
            self.allowed_types = tuple(allowed_types)
        if not self.allowed_types:
            self.allowed_types = (self.type,)

    def dictify(self, value, **kwargs):
        return value

    def undictify(self, value, **kwargs):
        try:
            return self.type(value)
        except (ValueError, TypeError):
            raise Invalid(self.error_msg)

    def validate(self, value, **kwargs):
        if not isinstance(value, self.allowed_types):
            raise Invalid(self.error_msg)


class String(TypeDictifier):
    '''
    >>> s = String()
    >>> s.undictify("foo")
    u'foo'
    >>> s.dictify("foo")
    'foo'
    >>> s.dictify(u"foo")
    u'foo'
    '''
    type = unicode
    # Undictify always returns unicode, but any string is valid.
    allowed_types = basestring

class Boolean(TypeDictifier):
    r"""
    >>> b = Boolean()
    >>> b.undictify(True)
    True
    >>> b.undictify('')
    False
    >>> # Note that this doesn't parse strings:
    >>> b.undictify('false')
    True
    >>> b.dictify(False)
    False
    >>> b.validate(True)
    >>> b.validate(False)
    >>> b.validate(1)
    Traceback (most recent call last):
    ...
    Invalid: type_error
    """
    type = bool

class Int(TypeDictifier):
    r"""
    >>> i = Int()
    >>> i.undictify('10')
    10
    >>> i.dictify(i.undictify('10'))
    10
    >>> i.undictify('10.0')
    Traceback (most recent call last):
    ...
    Invalid: type_error
    >>> i.undictify('one')
    Traceback (most recent call last):
    ...
    Invalid: type_error
    """
    type = int
    allowed_types = numbers.Integral

class Number(TypeDictifier):
    r"""
    >>> num = Number()
    >>> num.undictify('10')
    10.0
    >>> num.dictify(num.undictify('10'))
    10.0
    >>> num.undictify('10.1')
    10.1
    >>> num.dictify(num.undictify('10.1'))
    10.1
    >>> num.validate(1)
    >>> num.validate(1.1)
    >>> num.validate(1+1j)
    Traceback (most recent call last):
    ...
    Invalid: type_error
    >>> num.undictify('ten')
    Traceback (most recent call last):
    ...
    Invalid: type_error
    """
    type = float
    allowed_types = numbers.Real

class Complex(TypeDictifier):
    r"""
    >>> com = Complex()
    >>> com.undictify('10')
    (10+0j)
    >>> com.dictify(com.undictify('10+j'))
    (10+1j)
    >>> com.undictify('10.1-2.3j')
    (10.1-2.3j)
    >>> com.dictify(com.undictify('10.1'))
    (10.1+0j)
    >>> com.validate(1)
    >>> com.validate(1.1)
    >>> com.validate(1+1j)
    >>> com.undictify('ten')
    Traceback (most recent call last):
    ...
    Invalid: type_error
    """
    type = complex
    allowed_types = numbers.Complex

if __name__ == '__main__':
    import doctest
    doctest.testmod()