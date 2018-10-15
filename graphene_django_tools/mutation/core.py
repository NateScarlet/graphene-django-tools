"""Mutation tools. """

import sys
from collections import OrderedDict
from typing import Any, List

import graphene
from django import db
from graphene.types.mutation import MutationOptions
from graphql.execution.base import ResolveInfo

from dataclasses import dataclass

# pylint: disable=too-few-public-methods


class ModelMutationOptions(MutationOptions):
    """`Meta` for `ModelMutation`.  """

    model = None  # type: django.db.models.Model
    node_fieldname = None  # type: str
    require = ()  # type: tuple[str]
    exclude = ()  # type: tuple[str]


class ModelUpdateMutationOptions(ModelMutationOptions):
    """`Meta` for `ModelUpdateMutation`.  """

    id_fieldname = None  # type: str


@dataclass
class MutationContext:
    """Tuple data for mutation context.  """

    root: Any  # XXX: Not found documentation for this.
    info: ResolveInfo
    options: ModelMutationOptions
    arguments: dict


@dataclass
class ModelMutaionContext(MutationContext):
    """Tuple data for model mutation context.  """

    mapping: dict
    instance: graphene.ObjectType = None


@dataclass
class ModelBulkMutaionContext(MutationContext):
    """Tuple data for model bulk mutation context.  """

    fitlers: dict
    data: List[dict]
    query_set: db.models.QuerySet = None


def _sorted_dict(obj: dict, key=None, reverse=False)->OrderedDict:
    return OrderedDict(sorted(obj.items(), key=key, reverse=reverse))


def handle_resolve_error():
    """Detail message for `graphql.error.located_error.GraphQLLocatedError`.  """

    import traceback
    traceback.print_exc()
    type_, value, _ = sys.exc_info()

    raise Exception(f'{type_.__name__}:{value}')
