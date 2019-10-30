# -*- coding=UTF-8 -*-
"""Apollo-like resolver.  """

from __future__ import annotations
import typing

import django
import graphene
import graphql

from . import schema as schema_
from .. import texttools


def _nullable(
        v: graphene.types.unmountedtype.UnmountedType,
        is_nullable: bool = True
) -> graphene.types.unmountedtype.UnmountedType:
    ret = v
    if is_nullable and isinstance(ret, graphene.NonNull):
        ret = ret.of_type
    elif not is_nullable and not isinstance(ret, graphene.NonNull):
        ret = graphene.NonNull(ret)
    return ret


def _build_type(
        namespace: str,
        schema: typing.Any,
        mapping_bases: typing.Tuple[typing.Type, ...],
        is_mount=False,
) -> typing.Union[typing.Mapping, graphene.Scalar, graphene.ObjectType]:
    schema = schema_.FieldDefinition.parse(schema)
    is_input = graphene.InputObjectType in mapping_bases
    mount = schema.mount_as_argument if is_input else schema.mount_as_field

    field_type = schema.type

    # Mapping
    if schema.type is dict:
        field_type: typing.Type = type(
            texttools.camel_case(namespace),
            mapping_bases,
            {k: _build_type(
                f'{namespace}_{k}', v,
                mapping_bases=mapping_bases,
                is_mount=True
            ) for k, v in schema.child_definition.items()})

    # Iterable
    if schema.type is list:
        field_type = graphene.List(
            _nullable(_build_type(
                namespace,
                schema.child_definition,
                mapping_bases=mapping_bases,
            ), False),
        )

    if is_mount:
        return mount(type=field_type)
    return _nullable(field_type, not schema.required)


def _build_args_type(
        namespace: str,
        args: typing.Mapping,
) -> typing.Union[typing.Mapping, graphene.Scalar, graphene.ObjectType]:
    assert isinstance(
        args, typing.Mapping), f'Expected a mapping, got a {type(args)}'

    return {
        k: _build_type(
            namespace=f'{namespace}_{k}',
            schema=v,
            mapping_bases=(graphene.InputObjectType,),
            is_mount=True,
        )
        for k, v in args.items()
    }


class Resolver:
    """Apollo-like schema field resolver.  """

    # Resolver definitions.
    schema: typing.Optional[typing.Mapping] = None
    _field: typing.Optional[graphene.Field] = None

    # Data that avaliable inside `resolve`.
    parent: typing.Any
    info: graphql.execution.base.ResolveInfo
    context: django.core.handlers.wsgi.WSGIRequest

    def __init__(self,
                 parent: typing.Any,
                 info: graphql.execution.base.ResolveInfo):
        self.parent = parent
        self.info = info
        self.context = info.context

    def resolve(self, **kwargs):
        """Resolve the field.  """

        raise NotImplementedError(
            f'`{self.__class__.__name__}.resolve` is not implemented.')

    @classmethod
    def as_field(cls) -> graphene.Field:
        """Convert resolver as a graphene field.

        Returns:
            graphene.Field: Converted field.
        """

        if not cls.schema:
            raise NotImplementedError(
                f'Resolver schema is not defined: {cls.__name__}')
        if cls._field:
            return cls._field

        _type = _build_type(
            namespace=cls.__name__,
            schema=cls.schema,
            mapping_bases=(graphene.ObjectType,),
        )
        schema = schema_.FieldDefinition.parse(cls.schema)
        args_type = _build_args_type(
            cls.__name__,
            schema.args,
        ) if schema.args else None

        def resolver(parent, info, **kwargs):
            return cls(parent=parent, info=info).resolve(**kwargs)

        cls._field = graphene.Field(
            type=_type,
            args=args_type,
            description=schema.description,
            resolver=resolver,
            deprecation_reason=schema.deprecation_reason,
            required=False,
        )
        return cls._field
