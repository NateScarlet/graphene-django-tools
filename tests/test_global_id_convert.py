import pytest

import graphene_django_tools as gdtools


def test_str():
    assert gdtools.GlobalID.convert('VXNlcjox') == '1'


def test_list():
    assert gdtools.GlobalID.convert(['VXNlcjox', 'VXNlcjoy']) == ['1', '2']


def test_tuple():
    assert gdtools.GlobalID.convert(['VXNlcjox', 'VXNlcjoy']) == ['1', '2']


def test_validate_type_correct():
    assert gdtools.GlobalID.convert('VXNlcjox', 'User') == '1'


def test_validate_type_wrong():
    with pytest.raises(ValueError, match='Unexpected id type: expected=Person, actual=User.'):
        assert gdtools.GlobalID.convert('VXNlcjox', 'Person') == '1'
