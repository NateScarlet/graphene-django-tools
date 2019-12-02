"""Relay compatible connection resolver.  """
#pylint: disable=invalid-name

import graphene_django.fields as _gd_impl
from graphene_resolver.connection import (
    REGISTRY, build_schema as _build_schema, get_type, resolve as _resolve)

build_schema = _build_schema


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
    iterable = _gd_impl.maybe_queryset(iterable)
    if isinstance(iterable, _gd_impl.QuerySet):
        _len = iterable.count()
    else:
        _len = len(iterable)

    return _resolve(iterable, _len, **kwargs)

# TODO: remove at next minor version:
# pylint:disable=invalid-name


get_connection = get_type
resolve_connection = resolve
CONNECTION_REGISTRY = REGISTRY
