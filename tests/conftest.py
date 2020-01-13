import pytest
import graphene_django_tools as gdtools


@pytest.fixture(autouse=True)
def _clear_registry():
    gdtools.queryset.OPTIMIZATION_OPTIONS.clear()
