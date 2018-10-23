"""Mutation tools. """

from collections import OrderedDict
from typing import Any, List

import graphene
from django import db
from graphene.types.mutation import MutationOptions
from graphql.execution.base import ResolveInfo

from dataclasses import dataclass

# pylint: disable=too-few-public-methods


class NodeMutationOptions(MutationOptions):
    """`Meta` for `NodeMutation`.  """


class NodeUpdateMutationOptions(NodeMutationOptions):
    """`Meta` for `NodeUpdateMutation`.  """

    id_fieldname = None  # type: str


class ModelMutationOptions(NodeMutationOptions):
    """`Meta` for `ModelMutation`.  """

    model = None  # type: django.db.models.Model
    node_fieldname = None  # type: str
    require = ()  # type: tuple[str]
    exclude = ()  # type: tuple[str]
    require_mapping = True


class ModelUpdateMutationOptions(NodeUpdateMutationOptions, ModelMutationOptions):
    """`Meta` for `ModelUpdateMutation`.  """


@dataclass
class MutationContext:
    """Tuple data for mutation context.  """

    root: Any  # XXX: Not found documentation for this.
    info: ResolveInfo
    options: ModelMutationOptions
    arguments: dict


@dataclass
class NodeMutationContext(MutationContext):

    node: graphene.relay.Node


@dataclass
class ModelMutaionContext(NodeMutationContext):
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
