from base import Invalid, Field
from basic import Int, String
from schema import SchemaObj

from common_validators import InRange, OneOf, MatchesRegex

class Point(SchemaObj):
    field_types = {
        'x': Field(Int(), [InRange(0,10)]),
        'y': Field(Int(), [OneOf([1,2,3,4,5])]),
        'label': Field(String(), [MatchesRegex("foo[0-9]*")]),
    }

valid_str = {'x':'5', 'y':'3', 'label':'foo12'}
invalid_str = {'x':'-1', 'y':'0', 'label':'bar1'}
valid_data = {'x':5, 'y':3, 'label':'foo12'}
invalid_data = {'x':-1, 'y':0, 'label':'bar1'}

def test_valid():
    p = Point.undictify(valid_str)
    assert p.x == 5
    assert p.y == 3
    assert p.label == 'foo12'
    p.validate()
    assert p.dictify() == valid_data

def test_invalid():
    p = Point.undictify(invalid_str)
    assert p.x == -1
    assert p.y == 0
    assert p.label == 'bar1'
    assert p.dictify() == invalid_data
    expected_errors = dict(
        x = 'too_low',
        y = 'invalid_choice',
        label = 'invalid_string')
    try:
        p.validate(fail_early=True)
    except Invalid, e:
        assert not e.own_errors
        assert len(e.sub_errors) == 1, e
        k = e.sub_errors.keys()[0]
        assert e.sub_errors[k][0].message == expected_errors[k], e.sub_errors[k][0].message +' vs. '+ expected_errors[k]
    else:
        assert False, "Should have raised NestedInvalid!"
    try:
        p.validate()
    except Invalid, e:
        assert not e.own_errors
        assert len(e.sub_errors) == 3
        for k in expected_errors:
            assert e.sub_errors[k][0].message == expected_errors[k]
    else:
        assert False, "Should have raised NestedInvalid!"
