import pytest
import graphene_django_tools as gdtools


_DEFAULT_TYPE_REGISTRY = dict(gdtools.resolver.GRAPHENE_TYPE_REGISTRY)


@pytest.fixture(autouse=True)
def _clear_registry():
    gdtools.resolver.CONNECTION_REGISTRY.clear()
    gdtools.resolver.GRAPHENE_TYPE_REGISTRY.clear()
    gdtools.resolver.GRAPHENE_TYPE_REGISTRY.update(**_DEFAULT_TYPE_REGISTRY)
    gdtools.queryset.OPTIMIZATION_OPTIONS.clear()
