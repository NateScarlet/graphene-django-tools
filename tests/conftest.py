import graphene_django_tools as gdtools
import pytest


@pytest.fixture(autouse=True)
def _clear_registry():

    gdtools.resolver.resolver.RESOLVER_REGISTRY.clear()
