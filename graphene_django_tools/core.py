"""Addtional tools for `graphene_django`.  """
from typing import Type

import django
import graphene
import graphene_django
from graphene_django.registry import get_global_registry


def get_modelnode(model: Type[django.db.models.Model])\
        -> Type[graphene_django.DjangoObjectType]:
    """Get graphene node class from model class.

    Create one use default config if not created.

    Args:
        model (Type[django.db.models.Model])

    Returns:
        Type[graphene_django.DjangoObjectType]
    """

    registry = get_global_registry()
    ret = registry.get_type_for_model(model)
    if not ret:
        ret = create_modelnode(model)
    assert issubclass(ret, graphene_django.DjangoObjectType),\
        ret.__mro__
    return ret


def create_modelnode(cls: Type, bases=(), **meta_options) \
        -> Type[graphene_django.DjangoObjectType]:
    """Create node class for model class.

    Raises:
        AssertionError: node type already created.

    Returns:
        Type: Node type for model
    """

    from . import texttools
    meta_options.setdefault('model', cls)
    meta_options.setdefault('interfaces', (graphene.Node,))
    bases += (graphene_django.DjangoObjectType,)
    clsname = texttools.camel_case(f'{cls.__name__}Node')
    return type(clsname, bases, dict(Meta=meta_options))
