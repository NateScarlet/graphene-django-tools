# -*- coding=UTF-8 -*-
"""Apollo-like resolver.  """
# TODO: support enum

from __future__ import annotations
import dataclasses
import datetime
import decimal
import enum
import typing

import django
import graphene
import graphql

from . import core, texttools, types

TYPE_ALIAS = {
    str: graphene.String,
    int: graphene.Int,
    float: graphene.Float,
    bool: graphene.Boolean,
    enum.Enum: graphene.Enum,
    decimal.Decimal: graphene.Decimal,
    datetime.time: graphene.Time,
    datetime.date: graphene.Date,
    datetime.datetime: graphene.DateTime,
    datetime.timedelta: types.Duration,
    graphene.List: list,
    graphene.ObjectType: dict,
    graphene.InputObjectType: dict,
}


@dataclasses.dataclass
class SchemaFieldDefinition:
    """A mongoose-like schema for resolver.  """
    # Options:
    args: typing.Optional[typing.Mapping]  # only for root schema
    type: typing.Type
    required: bool
    description: typing.Optional[str]
    deprecation_reason: typing.Optional[str]

    # Parse results:
    child_definition: typing.Any

    @classmethod
    def parse(cls, v: typing.Any) -> SchemaFieldDefinition:
        """Parse a mongoose like schema

        Args:
            v (typing.Any): schema item

        Returns:
            SchemaDefinition: Parsing result
        """

        config = {}
        child_definition = None
        is_full_config = (
            isinstance(v, typing.Mapping)
            and 'type' in v
            and not (
                isinstance(v['type'], typing.Mapping)
                and isinstance(v['type'].get('type'), type)))

        if is_full_config:
            config.update(**v)
            if isinstance(v.get('type'), typing.Mapping):
                config['type'] = dict
                child_definition = v['type']
            elif isinstance(v.get('type'), typing.Iterable):
                config['type'] = list
                child_definition = v['type'][0]
        elif isinstance(v, typing.Mapping):
            config['type'] = dict
            child_definition = v
        elif isinstance(v, typing.Iterable):
            config['type'] = list
            child_definition = v[0]
        else:
            config['type'] = v
        if not isinstance(config['type'], type):
            raise SyntaxError(
                f'Invalid schema: can not find type field from: {v}')
        config['type'] = core.get_unmounted_type(config['type'])
        config['type'] = TYPE_ALIAS.get(config['type'], config['type'])

        config.setdefault('args', None)
        config.setdefault('required', False)
        config.setdefault('description', None)
        config.setdefault('deprecation_reason', None)

        return SchemaFieldDefinition(
            type=config['type'],
            required=config['required'],
            description=config['description'],
            deprecation_reason=config['deprecation_reason'],
            args=config['args'],
            child_definition=child_definition,
        )

    def mount_as_argument(self, **kwargs) -> graphene.Argument:
        """Get mounted graphene argument.

        Returns:
            graphene.Argument:
        """
        kwargs.setdefault('type', self.type)
        kwargs.setdefault('required', self.required)
        kwargs.setdefault('description', self.description)

        return graphene.Argument(**kwargs)

    def mount_as_field(self, **kwargs) -> graphene.Field:
        """Get mounted graphene field.

         Returns:
             graphene.Field:
        """
        kwargs.setdefault('type', self.type)
        kwargs.setdefault('required', self.required)
        kwargs.setdefault('description', self.description)
        kwargs.setdefault('deprecation_reason', self.deprecation_reason)
        if (issubclass(self.type, Resolver)):
            field = self.type.as_field()
            kwargs['type'] = core.get_unmounted_type(field)
            kwargs.setdefault('args', field.args)
            kwargs.setdefault('resolver', field.resolver)
            kwargs.setdefault('description', field.description)
            kwargs.setdefault('deprecation_reason', field.deprecation_reason)

        return graphene.Field(**kwargs)


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
    schema = SchemaFieldDefinition.parse(schema)
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
        schema = SchemaFieldDefinition.parse(cls.schema)
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
