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
