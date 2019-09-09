"""Mutation tools. """

from collections import OrderedDict
from dataclasses import dataclass
from typing import (TYPE_CHECKING, Any, Callable, Iterable, List, Optional,
                    Union)

import graphene
from django import db
from graphene.types.mutation import MutationOptions
from graphql.execution.base import ResolveInfo

# pylint: disable=too-few-public-methods

if TYPE_CHECKING:
    import django


class NodeMutationOptions(MutationOptions):
    """`Meta` for `NodeMutation`.  """

    node_fieldname = None  # type: Optional[str]


class NodeUpdateMutationOptions(NodeMutationOptions):
    """`Meta` for `NodeUpdateMutation`.  """

    id_fieldname = None  # type: Optional[str]


class NodeDeleteMutationOptions(NodeUpdateMutationOptions):
    """`Meta` for `NodeDeleteMutation`.  """

    allowed_cls: tuple = ()


class ModelMutationOptions(NodeMutationOptions):
    """`Meta` for `ModelMutation`.  """

    model = None  # type: django.db.models.Model
    fields = ()  # type: Union[Callable, Iterable]
    require = ()  # type: tuple[str]
    exclude = ()  # type: tuple[str]
    require_mapping = True


class ModelUpdateMutationOptions(NodeUpdateMutationOptions, ModelMutationOptions):
    """`Meta` for `ModelUpdateMutation`.  """


@dataclass
class MutationContext:
    """Tuple data for mutation context.  """

    root: Any  # parent node for this context.
    info: ResolveInfo
    options: MutationOptions
    arguments: dict


@dataclass
class NodeMutationContext(MutationContext):

    node: graphene.relay.Node
    options: NodeMutationOptions


@dataclass
class NodeUpdateMutationContext(MutationContext):
    options: NodeUpdateMutationOptions


@dataclass
class NodeDeleteMutationContext(MutationContext):
    options: NodeDeleteMutationOptions


@dataclass
class ModelMutationContext(NodeMutationContext):
    """Tuple data for model mutation context.  """

    mapping: dict
    options: ModelMutationOptions
    instance: graphene.ObjectType = None


@dataclass
class ModelBulkCreationMutationContext(MutationContext):
    """Tuple data for model bulk creation mutation context.  """

    data: List[dict]


@dataclass
class ModelBulkUpdateMutationContext(MutationContext):
    """Tuple data for model bulk update mutation context.  """
    mapping: dict
    query_set: db.models.QuerySet = None


def _sorted_dict(obj: dict, key=None, reverse=False) -> OrderedDict:
    return OrderedDict(sorted(obj.items(), key=key, reverse=reverse))
