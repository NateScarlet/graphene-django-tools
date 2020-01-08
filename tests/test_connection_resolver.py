# pylint:disable=missing-docstring,invalid-name,unused-variable

import django.db.models as djm
import pytest

import graphene_django_tools as gdtools

from . import models


@pytest.mark.django_db
def test_keep_queryset():

    result = gdtools.resolve_connection(models.Pet.objects.all(), first=1,)
    qs = result['nodes']
    assert isinstance(qs, djm.QuerySet)
    assert qs.model is models.Pet
