from base import Invalid
from basic import Int, String
from schema import SchemaObj

class Point(SchemaObj):
    field_types = {
        'x': Int(),
        'y': Int(),
        'label': String(),
    }
    def __init__(self, x, y, label='foo'):
        super(Point, self).__init__()
        self.x = x
        self.y = y
        self.label = label

plain_data = {'x':-12, 'y':1, 'label':'foo'}
blank_data = {}
bad_data = {'x':'hi', 'y':-1, 'label':'blarg'}
extra_data = {'x':-12, 'y':1, 'label':'foo', 'ex':['foo','bar'], 'ex2':'hi'}

def test_basic():
    p = Point.undictify(plain_data)
    assert p.x == -12
    assert p.y == 1
    assert p.label == 'foo'
    assert p.dictify() == plain_data, p.dictify()

def test_errors():
    try:
        Point.undictify(bad_data)
    except Invalid, e:
        assert e.sub_errors['x'][0].message == 'type_error'
    else:
        assert False

def test_ban_extra():
    StrictPoint = Point.subclass(extra_field_policy='error')
    try:
        StrictPoint.undictify(extra_data)
    except Invalid, e:
        assert len(e.own_errors) == 1
        err = e.own_errors[0]
        assert err.message == 'unexpected_fields'
        assert err.kwargs['keys'] == {'ex', 'ex2'}
    else:
        assert False

def test_construct():
    p = Point(-12,1)
    assert p.dictify() == plain_data


class TwoPoints(SchemaObj):
    field_types = dict(a=Point, b=Point)

def test_nested():
    x = TwoPoints.undictify(dict(a=plain_data, b=plain_data))
    assert x.a.x == x.b.x == -12
    assert x.dictify() == dict(a=plain_data, b=plain_data)
