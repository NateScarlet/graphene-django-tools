import pytest
import graphene_django_tools as gdtools


@pytest.fixture(autouse=True)
def _clear_registry():
    gdtools.resolver.CONNECTION_REGISTRY.clear()
