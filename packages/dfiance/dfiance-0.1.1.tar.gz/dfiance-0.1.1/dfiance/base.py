from error_aggregator import ErrorAggregator as _ErrAgg, NestedException


class SingleInvalid(Exception):
    '''Base class for all undictification errors.

    In general, self.message will be a string indicating the specific error,
    e.g. 'required' when a value is missing that shouldn't be, 'not_int' for
    a value that must be an integer but cannot be parsed as one, and so forth.
    The specific errors raised by various Dictifiers are class-specific.
    '''
    def __init__(self, message=None, **kwargs):
        if kwargs:
            super(SingleInvalid, self).__init__(message, kwargs)
        else:
            super(SingleInvalid, self).__init__(message)
        self.message = message
        self.kwargs = kwargs


class Invalid(NestedException):
    '''Base class for undictification errors of nested objects.

    This allows dictifiable types with sub-fields to record the errors from
    their subfields as well.
    '''
    def __init__(self, message=None, **kwargs):
        super(Invalid, self).__init__()
        if message or kwargs:
            self.own_errors.append(SingleInvalid(message, **kwargs))


class ErrorAggregator(_ErrAgg):
    '''Specialized ErrorAggregator to only aggregate Invalids'''
    error_type = Invalid
    catch_type = Invalid


class Validator(object):
    '''Abstract base class for Validators.'''
    def validate(self, value, **kwargs):
        return


class Dictifier(Validator):
    '''Abstract base class for Dictifiers.'''
    def dictify(self, value, **kwargs):
        raise NotImplementedError()

    def undictify(self, value, **kwargs):
        raise NotImplementedError()


class Field(Dictifier):
    '''Wrapper around a dictifier and an optional list of validators.

    A Field behaves like the dictifier handed to it on intialization, except in
    two respects:

    1. It handles None values
    2. It can have additional validators attached to it

    It passes None through dictify unchanged; on validation or undictifiance, it
    treats None as valid unless self.not_empty is True, in which case it raises
    Invalid("empty")

    If a list of validators is passed on initialization, then field.validate()
    will call each validator in order and raise a NestedInvalid with all of
    their exceptions if any of them fail.
    '''
    def __init__(self, dfier, vdators=(), not_empty=False):
        self.dfier = dfier
        self.vdators = tuple(vdators)
        self.not_empty = not_empty

    def dictify(self, value, **kwargs):
        if value is None:
            return None
        return self.dfier.dictify(value, **kwargs)

    def undictify(self, value, **kwargs):
        if value is None:
            if self.not_empty:
                raise Invalid("empty")
            return None
        return self.dfier.undictify(value, **kwargs)

    def validate(self, value, **kwargs):
        if value is None:
            if self.not_empty:
                raise Invalid("empty")
            return
        fail_early = kwargs.get("dfy_fail_early", False)
        error_agg = ErrorAggregator(autoraise = fail_early)
        with error_agg.checking():
            self.dfier.validate(value)
        for vdator in self.vdators:
            with error_agg.checking():
                vdator.validate(value)
        error_agg.raise_if_any()

    @classmethod
    def asfield(cls, dfier):
        '''Wrap a dictifier in a Field if it isn't already one.'''
        if isinstance(dfier, Field):
            return dfier
        return Field(dfier)

def _doctest_field_tests():
    '''
    Empty function so I can write tests in doctest form.

    >>> from basic import Int
    >>> field = Field(Int())
    >>> field.dictify(None)
    >>> field.undictify(None)
    >>> field.validate(None)
    >>> req_field = Field(Int(), not_empty=True)
    >>> req_field.dictify(None)
    >>> req_field.undictify(None)
    Traceback (most recent call last):
    ...
    Invalid: empty
    >>> req_field.validate(None)
    Traceback (most recent call last):
    ...
    Invalid: empty
    '''


if __name__ == '__main__':
    import doctest
    doctest.testmod()
