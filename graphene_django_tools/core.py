"""Addtional tools for `graphene_django`.  """
from typing import Type

import django
import graphene
import graphene_django
from graphene_django.registry import get_global_registry


def get_modelnode(model: Type[django.db.models.Model], is_autocreate=True)\
        -> Type[graphene_django.DjangoObjectType]:
    """Get graphene node class from model class.

    Args:
        model (Type[django.db.models.Model])
        is_autocreate (Boolean): Create modelnode type
            use default config if not created.

    Returns:
        Type[graphene_django.DjangoObjectType]
    """

    assert issubclass(model, django.db.models.Model), type(model)
    registry = get_global_registry()
    ret = registry.get_type_for_model(model)
    if not ret and is_autocreate:
        ret = create_modelnode(model)
    return ret


def create_modelnode(model: Type[django.db.models.Model], bases=(), **meta_options) \
        -> Type[graphene_django.DjangoObjectType]:
    """Create node class for model class.

    Raises:
        AssertionError: node type already created.

    Returns:
        Type: Node type for model
    """

    assert issubclass(model, django.db.models.Model), type(model)

    from . import texttools
    meta_options.setdefault('model', model)
    meta_options.setdefault('interfaces', (graphene.Node,))
    bases += (graphene_django.DjangoObjectType,)
    clsname = texttools.camel_case(f'{model.__name__}Node')
    return type(clsname, bases, dict(Meta=meta_options))
