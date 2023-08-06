import datetime

try:
    from dateutil.parser import parse as parse_datetime
    _have_dateutil = True
except ImportError:
    _have_dateutil = False

from base import Invalid, Dictifier

class DateTime(Dictifier):
    """
    Dictifier for datetimes.

    The 'format' argument determines what format will be used for serializing,
    and if the 'require_format' argument is True, only strings in that format
    will be deserialized. 'require_format' must be true if the dateutil module
    is not installed.

    If you have dateutil installed, however, then 'require_format' defaults to
    False, and DateTime will use dateutil.parser.parse to process dates, so any
    string dateutil can parse can be undictified:

    >>> dtfier = DateTime()
    >>> dtfier.undictify("12/25/2003")
    datetime.datetime(2003, 12, 25, 0, 0)
    >>> dtfier.undictify("12/25/2003 14:25:03.1")
    datetime.datetime(2003, 12, 25, 14, 25, 3, 100000)
    >>> dtfier.undictify("Dec 25, 2003 2:25:03.1 pm")
    datetime.datetime(2003, 12, 25, 14, 25, 3, 100000)


    Invalid strings get specific error messages:

    >>> dtfier.undictify("12/25/20003")
    Traceback (most recent call last):
    ...
    Invalid: bad_year
    >>> dtfier.undictify("13/25/2003")
    Traceback (most recent call last):
    ...
    Invalid: bad_month
    >>> dtfier.undictify("12/32/2003")
    Traceback (most recent call last):
    ...
    Invalid: bad_day
    >>> dtfier.undictify("12/25/2003 26:25:03.1")
    Traceback (most recent call last):
    ...
    Invalid: bad_hour
    >>> dtfier.undictify("12/25/2003 14:71:03.1")
    Traceback (most recent call last):
    ...
    Invalid: bad_minute
    >>> dtfier.undictify("12/25/2003 14:25:93.1")
    Traceback (most recent call last):
    ...
    Invalid: bad_second


    Non-numbers get generic "bad_format" error messages:

    >>> dtfier.undictify("12/hello/2003")
    Traceback (most recent call last):
    ...
    Invalid: bad_format
    >>> dtfier.undictify("Not even remotely a datetime.")
    Traceback (most recent call last):
    ...
    Invalid: bad_format
    >>> dtfier.undictify(["this", "isn't", "even", "a", "string"])
    Traceback (most recent call last):
    ...
    Invalid: type_error


    Dictifying will serialize to self.format, which defaults to
    "%m/%d/%Y %H:%M:%S.%f" but can be set to anything.

    >>> d = datetime.datetime(2003, 12, 25, 14, 21, 3, 100500)
    >>> DateTime().dictify(d)
    u'12/25/2003 14:21:03.100500'
    >>> DateTime(format='%I:%M:%S.%f%p on %h %e, %Y').dictify(d)
    u'02:21:03.100500PM on Dec 25, 2003'


    Be warned, though, that you can fail at formatting by entering something
    which neither datetime.strptime nor dateutil can parse:

    >>> dumb_format = 'At %I:%M:%S.%f%p on day number %e of the year %Y, in %h'
    >>> dtfier = DateTime(format=dumb_format)
    >>> dtfier.dictify(d)
    u'At 02:21:03.100500PM on day number 25 of the year 2003, in Dec'
    >>> dtfier.undictify(dtfier.dictify(d))
    Traceback (most recent call last):
    ...
    Invalid: bad_format


    Or by entering something that throws away data:

    >>> dtfier = DateTime(format="%h %e %Y")
    >>> dtfier.dictify(d)
    u'Dec 25 2003'
    >>> dtfier.undictify(dtfier.dictify(d))
    datetime.datetime(2003, 12, 25, 0, 0)
    >>> dtfier.undictify(dtfier.dictify(d)) == d
    False


    Validate only approves of datetimes:

    >>> DateTime().validate(datetime.datetime.now())
    >>> DateTime().validate("")
    Traceback (most recent call last):
    ...
    Invalid: type_error


    Like all good dictifiers, undictify is idempotent:

    >>> dtfier = DateTime()
    >>> dt = dtfier.undictify("1/1/2003")
    >>> dtfier.undictify(dt) == dt
    True
    """
    _dt_type = datetime.datetime

    def __init__(self, format="%m/%d/%Y %H:%M:%S.%f", require_format=not _have_dateutil):
        self.format = format
        if not require_format and not _have_dateutil:
            msg = ("Can't parse dates or times with require_format=False"
                   " unless dateutil is installed.")
            raise ValueError(msg)

    def parse_datetime(self, value):
        '''Parse a formatted datetime.

        Tries datetime.datetime.strptime; if that fails it falls back to
        dateutil if present.
        '''
        if not isinstance(value, basestring):
            raise Invalid("type_error")
        try:
            return datetime.datetime.strptime(value, self.format)
        except ValueError, e:
            if not _have_dateutil:
                raise Invalid("bad_format")
        # If we get here, then we have dateutil - try to use it!
        try:
            return parse_datetime(value)
        except ValueError, e:
            if e.message.lower() == 'year is out of range':
                raise Invalid("bad_year")
            elif e.message.lower() == 'month must be in 1..12':
                raise Invalid("bad_month")
            elif e.message.lower() == 'day is out of range for month':
                raise Invalid("bad_day")
            elif e.message.lower() == 'hour must be in 0..23':
                raise Invalid('bad_hour')
            elif e.message.lower() == 'minute must be in 0..59':
                raise Invalid('bad_minute')
            elif e.message.lower() == 'second must be in 0..59':
                raise Invalid('bad_second')
            else:
                raise Invalid("bad_format")

    def undictify(self, value, **kwargs):
        if isinstance(value, self._dt_type):
            return value
        return self.parse_datetime(value)

    def validate(self, value):
        if not isinstance(value, self._dt_type):
            raise Invalid("type_error")

    def dictify(self, value):
        return unicode(value.strftime(self.format))

class Date(DateTime):
    """
    Dictifier for dates.

    All the notes about DateTime apply:

    Dateutil parsing:

    >>> date = Date()
    >>> date.undictify("12/25/2003")
    datetime.date(2003, 12, 25)

    Error msgs for each field that can fail, contingent on dateutil recognizing
    that something is the field in question:

    >>> date.undictify("13/25/2003")
    Traceback (most recent call last):
    ...
    Invalid: bad_month
    >>> date.undictify("12/32/2003")
    Traceback (most recent call last):
    ...
    Invalid: bad_day
    >>> date.undictify("12/25/20003")
    Traceback (most recent call last):
    ...
    Invalid: bad_year
    >>> date.undictify("12/hi/2003")
    Traceback (most recent call last):
    ...
    Invalid: bad_format
    >>> date.undictify("Not a date")
    Traceback (most recent call last):
    ...
    Invalid: bad_format

    Formats work, but don't choose something dateutil can't read back:

    >>> date = datetime.date(2003, 12, 25)
    >>> datefier = Date(format="%h %e '%g")
    >>> datefier.dictify(date)
    u"Dec 25 '03"
    >>> datefier.undictify(datefier.dictify(date))
    datetime.date(2003, 12, 25)
    >>> datefier = Date(format="Day %e of month %h in the year %g")
    >>> datefier.dictify(date)
    u'Day 25 of month Dec in the year 03'
    >>> datefier.undictify(datefier.dictify(date))
    Traceback (most recent call last):
    ...
    Invalid: bad_format

    Validate passes only dates:

    >>> Date().validate(datetime.date.today())
    >>> Date().validate(datetime.time())
    Traceback (most recent call last):
    ...
    Invalid: type_error

    As a side effect of dateutil, the Date dictifier WILL undictify strings
    dateutil parses as full datetimes, discarding the time:

    >>> Date().undictify('12/25/2003 14:21:03.100500')
    datetime.date(2003, 12, 25)
    """

    _dt_type = datetime.date

    def __init__(self, format="%m/%d/%Y"):
        super(Date, self).__init__(format)

    def undictify(self, value, **kwargs):
        if isinstance(value, self._dt_type):
            return value
        return self.parse_datetime(value).date()

class Time(DateTime):
    """
    >>> Time().undictify("14:25:03.1")
    datetime.time(14, 25, 3, 100000)
    >>> Time().undictify("26:25:03.1")
    Traceback (most recent call last):
    ...
    Invalid: bad_hour
    >>> Time().undictify("14:71:03.1")
    Traceback (most recent call last):
    ...
    Invalid: bad_minute
    >>> Time().undictify("14:25:93.1")
    Traceback (most recent call last):
    ...
    Invalid: bad_second
    >>> Time().undictify("Not a time")
    Traceback (most recent call last):
    ...
    Invalid: bad_format
    >>> Time().dictify(datetime.time(14, 25, 3, 100000))
    u'14:25:03.100000'
    >>> Time(format="%I:%M%p").dictify(datetime.time(14, 25, 3, 1))
    u'02:25PM'
    >>> Time().undictify(datetime.time(14, 25, 3, 1))
    datetime.time(14, 25, 3, 1)

    """
    _dt_type = datetime.time

    def __init__(self, format="%H:%M:%S.%f"):
        super(Time, self).__init__(format)

    def undictify(self, value, **kwargs):
        if isinstance(value, self._dt_type):
            return value
        return self.parse_datetime(value).time()

if __name__ == '__main__':
    import doctest
    doctest.testmod()