# -*- coding=UTF-8 -*-
"""Mongoose-like schema.  """

from __future__ import annotations
import functools
import typing

import graphene

from . import schema as schema_
from .. import texttools, types

GRAPHENE_TYPE_REGISTRY: typing.Dict[
    str,
    graphene.types.unmountedtype.UnmountedType
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


def dynamic_type(type_: typing.Any, registry=None) -> typing.Callable:
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
        assert isinstance(type_, type), type_
        return type_

    return functools.partial(type_fn, type_)


def nullable(
        v: graphene.types.unmountedtype.UnmountedType,
        is_nullable: bool = True
) -> graphene.types.unmountedtype.UnmountedType:
    """Modify nullable of a unmounted field type.

    Args:
        v (graphene.types.unmountedtype.UnmountedType): Field type.
        is_nullable (bool, optional): Desired value. Defaults to True.

    Returns:
        graphene.types.unmountedtype.UnmountedType: Modified value.
    """
    ret = v
    if is_nullable and isinstance(ret, graphene.NonNull):
        ret = ret._of_type
    elif not is_nullable and not isinstance(ret, graphene.NonNull):
        ret = graphene.NonNull(ret)
    return ret


def build_type(
        namespace: str,
        schema: typing.Any,
        mapping_bases: typing.Tuple[typing.Type, ...],
        is_mount=False,
        registry=None,
) -> graphene.utils.orderedtype.OrderedType:
    """Build field type from schema.

    Args:
        namespace (str): Namespace for auto naming.
        schema (typing.Any): Supported schema value.
        mapping_bases (typing.Tuple[typing.Type, ...]): Class bases for mapping field.
        is_mount (bool, optional): Whether returns mounted field. Defaults to False.
        registry (typing.Dict, optional): Graphene type registry.
            Defaults to `schema_.GRAPHENE_TYPE_REGISTRY`.

    Returns:
        graphene.utils.orderedtype.OrderedType: Graphene field type.
    """
    registry = registry or GRAPHENE_TYPE_REGISTRY
    schema = schema_.FieldDefinition.parse(schema)
    is_input = graphene.InputObjectType in mapping_bases
    mount = schema.mount_as_argument if is_input else schema.mount_as_field

    field_type = schema.type

    # Mapping
    if schema.type is dict:
        name = schema.name or texttools.camel_case(namespace)
        field_type: typing.Type = type(
            name,
            mapping_bases,
            {
                **{
                    k: build_type(
                        f'{namespace}_{k}', v,
                        mapping_bases=mapping_bases,
                        is_mount=True
                    ) for k, v in schema.child_definition.items()
                },
                **dict(
                    Meta=dict(
                        interfaces=schema.interfaces
                    )
                )
            })
        registry[name] = field_type

    # Iterable
    if schema.type is list:
        field_type = graphene.List(
            nullable(build_type(
                namespace,
                schema.child_definition,
                mapping_bases=mapping_bases,
            ), False),
        )

    if is_mount:
        return mount(type=field_type)
    return nullable(field_type, not schema.required)


def build_args_type(
        namespace: str,
        args: typing.Mapping,
) -> typing.Mapping[str, typing.Union[graphene.Scalar, graphene.InputObjectType]]:
    """Build type for args.

    Args:
        namespace (str): Namespace for auto naming.
        args (typing.Mapping): Mapping for args schema.

    Returns:
        typing.Mapping[str, typing.Union[graphene.Scalar, graphene.InputObjectType]]:
            Graphene args field mapping.
    """
    assert isinstance(
        args, typing.Mapping), f'Expected a mapping, got a {type(args)}'

    return {
        k: build_type(
            namespace=f'{namespace}_{k}',
            schema=v,
            mapping_bases=(graphene.InputObjectType,),
            is_mount=True,
        )
        for k, v in args.items()
    }
