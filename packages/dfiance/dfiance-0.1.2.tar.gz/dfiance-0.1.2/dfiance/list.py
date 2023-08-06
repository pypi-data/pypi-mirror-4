from base import Dictifier, ErrorAggregator, Invalid, Field

class List(Dictifier):
    '''Dictifier for homogenous lists

    The argument elt_type is the dictifier for the elements in the list; if it
    is not a Field, it will be wrapped in one.

    The arugment required determines the generated Field's not_empty flag. It is
    ignored if elt_type is a subclass of Field.

    For example:

    >>> from basic import Int
    >>> l = List(Int())
    >>> l.undictify(["1", "4", 5])
    [1, 4, 5]
    >>> l.dictify([1, 2, 3])
    [1, 2, 3]
    >>> l.validate([1, 2, 3])

    By default empty values are not allowed:

    >>> l.validate([1, None, 'hi'])
    Traceback (most recent call last):
    ...
    Invalid: 1: [empty], 2: [type_error]

    These two are equivalent:

    >>> l1 = List(Field(Int(), not_empty=False))
    >>> l2 = List(Int(), required=False)
    >>> l1.validate([1, None, 3])
    >>> l2.validate([1, None, 3])
    '''
    def __init__(self, elt_type, required=True):
        if not isinstance(elt_type, Field):
            elt_type = Field(elt_type, not_empty=required)
        self.elt_type = elt_type

    def undictify(self, value, **kwargs):
        # If _full_errors is True, then gather all errors from this and its
        # children. Otherwise, just raise the first error we encounter.
        error_agg = ErrorAggregator(autoraise = kwargs.get('fail_early', False))
        result = []
        for i, item in enumerate(value):
            with error_agg.checking_sub(str(i)):
                result.append(self.elt_type.undictify(item, **kwargs))
        error_agg.raise_if_any()
        return result

    def dictify(self, value, **kwargs):
        return [self.elt_type.dictify(x, **kwargs) for x in value]

    def validate(self, value, **kwargs):
        error_agg = ErrorAggregator(autoraise = kwargs.get('fail_early', False))
        try:
            iterator = iter(value)
        except TypeError: # item isn't iterable!
            raise Invalid("type_error")
        for i, item in enumerate(iterator):
            with error_agg.checking_sub(str(i)):
                self.elt_type.validate(item)
        error_agg.raise_if_any()


if __name__ == '__main__':
    import doctest
    doctest.testmod()
