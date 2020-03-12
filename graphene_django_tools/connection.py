"""Relay compatible connection resolver.  """
# pylint: disable=invalid-name

import re
import typing

import django.db.models as djm
import graphql
import lazy_object_proxy as lazy
from graphene_resolver.connection import REGISTRY as _REGISTRY
from graphene_resolver.connection import _get_node_name
from graphene_resolver.connection import build_schema as _build_schema
from graphene_resolver.connection import get_type as _get_type
from graphene_resolver.connection import resolve as _resolve
from graphene_resolver.connection import resolver

from . import queryset as qs_
from .resolver import Resolver

build_schema = _build_schema
REGISTRY = _REGISTRY


def set_optimization_default(
        node: typing.Union[resolver.Resolver, str, typing.Any],
        *,
        edge_name: str = None
) -> None:
    """Set optimization default for connection.

    Args:
        node (typing.Union[resolver.Resolver, str, typing.Any]):
            Connection resolver or name or schema.
    """

    name = _get_node_name(node)
    edge_name = edge_name or f"{re.sub('Connection$', '', name)}Edge"

    opt = qs_.OPTIMIZATION_OPTIONS.setdefault(name, {})
    opt.setdefault('related', {'nodes': 'self', 'edges': 'self', })

    opt = qs_.OPTIMIZATION_OPTIONS.setdefault(edge_name, {})
    opt.setdefault('related', {'node': 'self'})


def get_type(
        node: typing.Union[resolver.Resolver, str, typing.Any],
        *,
        name: str = None,
) -> resolver.Resolver:
    """Get connection resolver from registry, and set default optimization options.
    one will be created with `build_schema` if not found in registry.

    Args:
        node (typing.Union[resolver.Resolver, str, typing.Any]): Node resolver or schema.
        name (str, optional): Override default connection name,
            required when node name is not defined.

    Returns:
        resolver.Resolver: Created connection resolver, same name will returns same resolver.
    """

    ret = _get_type(node, name=name)
    set_optimization_default(ret)
    return ret


def resolve(
        iterable,
        **kwargs,
) -> dict:
    """Resolve iterable to connection

    Args:
        iterable (typign.Iterable): value

    Returns:
        dict: Connection data.
    """

    if isinstance(iterable, djm.Manager):
        iterable = iterable.all()

    if isinstance(iterable, djm.QuerySet):
        _len = lazy.Proxy(iterable.count)
    else:
        _len = len(iterable)

    return _resolve(iterable, _len, **kwargs)


def optimized_resolve(
        info: graphql.ResolveInfo,
        queryset: djm.QuerySet,
        **kwargs,
) -> dict:
    """Resolve django queryset base on query selection.
    And prime dataloader cache.

    Args:
        info (graphql.ResolveInfo): Resolve info.
        queryset (djm.QuerySet): Queryset to resolve.

    Returns:
        dict: Connection resolve result.
    """

    qs = qs_.optimize(queryset.all(), info)
    ret = resolve(qs, **kwargs)

    def _prime_nodes(v):
        for i in v:
            # Prime dataloader cache
            Resolver(info=info).resolve_gid(i)
        return v
    nodes = ret['nodes']
    ret['nodes'] = lazy.Proxy(lambda: _prime_nodes(nodes))
    return ret
