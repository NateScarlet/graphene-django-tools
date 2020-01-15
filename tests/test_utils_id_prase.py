
import pytest

import graphene_django_tools as gdtools


def test_valid():
    _id = gdtools.utils.ID.parse('VXNlcjox')
    assert _id.type == 'User'
    assert _id.value == '1'


def test_invalid():
    with pytest.raises(ValueError, match='Invalid id: value=User:1'):
        gdtools.utils.ID.parse('User:1')
