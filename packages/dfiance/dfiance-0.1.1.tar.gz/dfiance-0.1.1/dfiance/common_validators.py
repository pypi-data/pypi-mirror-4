import re

from base import Invalid, Validator

class InRange(Validator):
    '''Require non-empty values to be between two endpoints.

    The endpoints themselves are allowed.

    >>> from basic import Int
    >>> from base import Field
    >>> RangeInt = Field(Int(), [InRange(0, 5)])
    >>> RangeInt.validate(0)
    >>> RangeInt.validate(3)
    >>> RangeInt.validate(5)
    >>> RangeInt.validate(None)
    >>> RangeInt.validate(-1)
    Traceback (most recent call last):
        ...
    Invalid: too_low
    >>> RangeInt.validate(6)
    Traceback (most recent call last):
        ...
    Invalid: too_high

    Note that the types can be any type for which < and > are defined:

    >>> from datetypes import Date
    >>> from datetime import date
    >>> from base import Field
    >>> range = InRange(date(2012, 1, 1), date(2012, 12, 31))
    >>> DateIn2012 = Field(Date(), [range])
    >>> DateIn2012.validate(date(2012, 4, 13))
    >>> DateIn2012.validate(date(2013, 1, 1))
    Traceback (most recent call last):
        ...
    Invalid: too_high
    '''
    def __init__(self, low=None, high=None):
        self.low = low
        self.high = high

    def validate(self, value, **kwargs):
        if value is None: return
        if self.low is not None and value < self.low:
            raise Invalid("too_low")
        if self.high is not None and value > self.high:
            raise Invalid("too_high")

class OneOf(Validator):
    '''Require non-empty values to come from a fixed list of options.

    >>> from basic import String
    >>> from base import Field
    >>> Baggins = Field(String(), [OneOf(['Frodo', 'Bilbo'])])
    >>> Baggins.validate("Bilbo")
    >>> Baggins.validate("Frodo")
    >>> Baggins.validate("Meriadoc")
    Traceback (most recent call last):
        ...
    Invalid: invalid_choice
    '''
    def __init__(self, options):
        self.options = options

    def validate(self, value, **kwargs):
        if value is None: return
        if value not in self.options:
            raise Invalid("invalid_choice")

class MatchesRegex(Validator):
    '''Require non-empty values to match a regular expression.

    >>> from basic import String
    >>> from base import Field
    >>> IP = Field(String(), vdators=[MatchesRegex("\d{1,3}(\.\d{1,3}){3}")])
    >>> IP.validate("127.0.0.1")
    >>> IP.validate("This is not an IP address.")
    Traceback (most recent call last):
        ...
    Invalid: invalid_string
    >>> IP.validate("127.0.0.no")
    Traceback (most recent call last):
        ...
    Invalid: invalid_string
    '''
    def __init__(self, regex):
        self.regex = re.compile(regex)

    def validate(self, value, **kwargs):
        if value is None: return
        if not self.regex.match(value):
            raise Invalid("invalid_string")


if __name__ == '__main__':
    import doctest
    doctest.testmod()
