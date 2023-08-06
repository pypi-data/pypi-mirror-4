from base import Invalid, ErrorAggregator, Field
from dictifiable import Dictifiable
from subclass import Subclassable

def overlay(d1, d2, strip_none=True):
    '''Return a copy of d1 with d2 overlaid.

    If strip_none is False, this is equivalent to `d1.copy().update(d2)`.

    If strip_none is True, then any keys of d2 that map to None will be deleted
    from d1.
    '''
    x = d1.copy();
    x.update(d2)
    if strip_none:
        for key, value in d2.iteritems():
            if value is None:
                del x[key]
    return x

class SchemaObj(Subclassable, Dictifiable):
    extra_field_policy = "ignore"
    field_types = dict()

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    @classmethod
    def __subclass__(cls, field_types={}, **kwargs):
        '''Subclass this object.

        field_types will overlay any field_types set on this class. If
        field_types includes a pair (key, None), then field_types[key] will be
        deleted.
        '''
        super(SchemaObj, cls).__subclass__(**kwargs)
        cls.field_types = overlay(cls.field_types, field_types)
        for key, field_or_dfier in cls.field_types.iteritems():
            cls.field_types[key] = Field.asfield(field_or_dfier)

    def _handle_fields(self, value, error_agg, kwargs):
        '''Undictify our fields. Override this to customize subfields.'''
        for key, type in self.field_types.iteritems():
            with error_agg.checking_sub(key):
                val = value.get(key, None)
                setattr(self, key, type.undictify(val, **kwargs))

    def _handle_extras(self, value, error_agg, kwargs):
        '''Process any keys in value that aren't expected fields.

        If self.extra_field_policy is 'error', these extra values will be added
        as errors. Otherwise they'll be discarded.
        '''
        if self.extra_field_policy != 'error':
            return
        extra_keys = set(value.keys()) - set(self.field_types.keys())
        if extra_keys:
            error_agg.own_error(Invalid('unexpected_fields', keys=extra_keys))

    def __undictify__(self, value, **kwargs):
        if value is None:
            value = {}
        if not isinstance(value, dict):
            raise Invalid('not_dict')
        # If fail_early is True, then gather all errors from this and its
        # children. Otherwise, just raise the first error we encounter.
        error_agg = ErrorAggregator(autoraise = kwargs.get('fail_early', False))
        self._handle_fields(value, error_agg, kwargs)
        self._handle_extras(value, error_agg, kwargs)
        error_agg.raise_if_any()

    def __dictify__(self, **kwargs):
        result = {}
        for key, typ in self.field_types.items():
            result[key] = typ.dictify(getattr(self, key))
        return result

    def __validate__(self, **kwargs):
        error_agg = ErrorAggregator(autoraise = kwargs.get('fail_early', False))
        for field, type in self.field_types.iteritems():
            with error_agg.checking_sub(field):
                try:
                    val = getattr(self, field)
                except AttributeError:
                    raise Invalid("missing_field", name=field)
                type.validate(val)
        error_agg.raise_if_any()

    def dictify(self, **kwargs):
        return self.dfier().dictify(self, **kwargs)

    @classmethod
    def undictify(cls, value, **kwargs):
        return cls.dfier().undictify(value, **kwargs)

    def validate(self, **kwargs):
        return self.dfier().validate(self, **kwargs)


class DeclSchemaObj(SchemaObj):
    '''SchemaObj that automatically adds all Field class members to field_types.

    This is useful if you want to use SchemaObjs as mixins:

    >>> from basic import Int, String
    >>> class Point(DeclSchemaObj):
    ...   x = Field(Int())
    ...   y = Field(Int())
    >>> Point.field_types['x'] is Point.x
    True
    >>> Point.field_types['y'] is Point.y
    True
    >>> Point(x=1, y=3).dictify() == dict(x=1, y=3)
    True
    >>> class Labeled(DeclSchemaObj):
    ...   label = Field(String())
    >>> Labeled(label='hi').dictify() == dict(label='hi')
    True
    >>> class LabeledPoint(Labeled, Point):
    ...   pass
    >>> lp = LabeledPoint.undictify(dict(x='1', y='3', label='foo'))
    >>> lp.x, lp.y, lp.label
    (1, 3, u'foo')

    '''
    @classmethod
    def __subclass__(cls, **kwargs):
        super(DeclSchemaObj, cls).__subclass__(**kwargs)
        for key in dir(cls):
            val = getattr(cls, key)
            if isinstance(val, Field):
                cls.field_types[key] = val

if __name__ == '__main__':
    import doctest
    doctest.testmod()
