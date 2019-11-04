# -*- coding=UTF-8 -*-
"""Mongoose-like schema.  """

from __future__ import annotations
import functools
import typing

import graphene

from .. import types

GRAPHENE_TYPE_REGISTRY: typing.Dict[
    str,
    typing.Type[graphene.types.unmountedtype.UnmountedType]
] = {
    'ID': graphene.ID,
    'Boolean': graphene.Boolean,
    'String': graphene.String,
    'Int': graphene.Int,
    'Float': graphene.Float,
    'Decimal': graphene.Decimal,
    'Time': graphene.Time,
    'Date': graphene.Date,
    'DateTime': graphene.DateTime,
    'Duration': types.Duration,
}


def dynamic_type(type_: typing.Any, *, registry=None) -> typing.Callable:
    """Get dynamic type function for given typename.

    Args:
        type_ (typing.Any): typename or type itself.
        registry (typing.Dict, optional): Graphene type registry. Defaults to None.

    Returns:
        typing.Callable: dynamic type function
    """
    registry = registry or GRAPHENE_TYPE_REGISTRY

    def type_fn(type_, *_args, **_kwargs):
        if isinstance(type_, str):
            type_ = registry[type_]

        assert (isinstance(type_, type)), repr(type_)
        return type_

    return functools.partial(type_fn, type_)
