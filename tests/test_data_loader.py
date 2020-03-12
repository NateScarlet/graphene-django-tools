# pylint:disable=missing-docstring,invalid-name,unused-variable

import pytest

import graphene_django_tools as gdtools

from . import models

pytestmark = [pytest.mark.django_db]


def test_integer_key(django_assert_num_queries):
    reporter1 = models.Reporter.objects.create(
        first_name='reporter1',
    )
    reporter2 = models.Reporter.objects.create(
        first_name='reporter2',
    )
    loader = gdtools.dataloader.get_for_model(models.Reporter)
    with django_assert_num_queries(1):
        assert loader.load(reporter1.pk).get() == reporter1
    with django_assert_num_queries(0):
        assert loader.load(str(reporter1.pk)).get() == reporter1
