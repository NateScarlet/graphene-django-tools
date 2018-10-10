"""Mutation tools. """

import re
from collections import OrderedDict
from typing import Any, NamedTuple, Type

import django
import graphene_django
import graphene_django.forms.mutation
from graphene.types.mutation import MutationOptions
from graphene_django.registry import get_global_registry
from graphql.execution.base import ResolveInfo


def get_model_nodetype(model: Type[django.db.models.Model])\
        -> Type[graphene_django.DjangoObjectType]:
    """Get graphene node class from model clsss.

    Args:
        model (Type[django.db.models.Model])

    Returns:
        Type[graphene_django.DjangoObjectType]
    """

    registry = get_global_registry()
    ret = registry.get_type_for_model(model)
    if not ret:
        ret = type(
            re.sub('Type$|$', 'Type', model.__name__),
            (graphene_django.DjangoObjectType,),
            dict(Meta=dict(model=model)))
    assert issubclass(ret, graphene_django.DjangoObjectType),\
        ret.__mro__
    return ret

# pylint: disable=too-few-public-methods


class ModelMutationOptions(MutationOptions):
    """`Meta` for `DjangoModelMutation`.  """

    model = None  # type: django.db.models.Model
    nodename = None  # type: str
    require_arguments = ()  # type: tuple[str]
    exclude_arguments = ()  # type: tuple[str]


class MutationContext(NamedTuple):
    """Tuple data for mutation context.  """

    root: Any  # XXX: Not found documentation for this.
    info: ResolveInfo
    meta: ModelMutationOptions
    data: dict


def _sorted_dict(obj: dict, key=None, reverse=None)->OrderedDict:
    return OrderedDict(sorted(obj.items(), key=key, reverse=reverse))
