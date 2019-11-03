# -*- coding=UTF-8 -*-
"""Mongoose-like schema.  """

from __future__ import annotations
import dataclasses
import datetime
import decimal
import typing

import django.db.models
import graphene
import graphene_django.converter
import graphene_django.registry

from .. import core, types

TYPE_ALIAS = {
    str: graphene.String,
    int: graphene.Int,
    float: graphene.Float,
    bool: graphene.Boolean,
    decimal.Decimal: graphene.Decimal,
    datetime.time: graphene.Time,
    datetime.date: graphene.Date,
    datetime.datetime: graphene.DateTime,
    datetime.timedelta: types.Duration,
    graphene.List: list,
    graphene.ObjectType: dict,
    graphene.InputObjectType: dict,
    'ID': graphene.ID,
    'Boolean': graphene.Boolean,
    'String': graphene.String,
    'Int': graphene.Int,
    'Float': graphene.Float,
    'Duration': types.Duration,
    'Date': graphene.DateTime,
}


@dataclasses.dataclass
class FieldDefinition:
    """A mongoose-like schema for resolver field.  """

    # Options:
    args: typing.Mapping
    type: typing.Type
    required: bool
    name: typing.Optional[str]
    interfaces: typing.Iterable[graphene.Interface]
    description: typing.Optional[str]
    deprecation_reason: typing.Optional[str]

    # Parse results:
    child_definition: typing.Any

    @classmethod
    def parse(cls, v: typing.Any) -> FieldDefinition:
        """Parse a mongoose like schema

        Args:
            v (typing.Any): schema item

        Returns:
            SchemaDefinition: Parsing result
        """
        from . import resolver

        config = {}
        config.setdefault('args', {})
        config.setdefault('required', False)
        config.setdefault('name', None)
        config.setdefault('description', None)
        config.setdefault('deprecation_reason', None)
        config.setdefault('interfaces', ())
        child_definition = None
        is_full_config = (
            isinstance(v, typing.Mapping)
            and 'type' in v
            and not (
                isinstance(v['type'], typing.Mapping)
                and isinstance(v['type'].get('type'), (type, str, django.db.models.Field))))

        type_def = v
        if is_full_config:
            config.update(**v)
            type_def = v['type']
        if isinstance(type_def, django.db.models.Field):
            config['type'] = graphene_django.converter.convert_django_field_with_choices(
                type_def,
                registry=graphene_django.registry.get_global_registry()).__class__
        elif isinstance(type_def, str):
            if type_def[-1] == '!':
                config.setdefault('required', True)
                type_def = type_def[:-1]
            config['type'] = TYPE_ALIAS[type_def]
        elif isinstance(type_def, typing.Mapping):
            config['type'] = dict
            child_definition = type_def
        elif isinstance(type_def, typing.Iterable):
            config['type'] = list
            child_definition = type_def[0]
        else:
            config['type'] = type_def
        config['type'] = TYPE_ALIAS.get(config['type'], config['type'])
        if not isinstance(config['type'], type):
            raise SyntaxError(
                f'Invalid schema: can not find type field from: {v}')
        if isinstance(config['type'], graphene.types.mountedtype.MountedType):
            mounted = config['type']
            config['type'] = core.get_unmounted_type(mounted)
        # Merge root level resolver args.
        if issubclass(config['type'], resolver.Resolver):
            args = dict(cls.parse(config['type'].schema).args)
            args.update(**config['args'])
            config['args'] = args

        return cls(
            type=config['type'],
            required=config['required'],
            name=config['name'],
            description=config['description'],
            deprecation_reason=config['deprecation_reason'],
            args=config['args'],
            interfaces=config['interfaces'],
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
        from . import resolver

        kwargs.setdefault('type', self.type)
        kwargs.setdefault('required', self.required)
        kwargs.setdefault('description', self.description)
        kwargs.setdefault('deprecation_reason', self.deprecation_reason)
        if issubclass(self.type, resolver.Resolver):
            field = self.type.as_field()
            kwargs['type'] = core.get_unmounted_type(field)
            kwargs.setdefault('args', field.args)
            kwargs.setdefault('resolver', field.resolver)
            kwargs.setdefault('description', field.description)
            kwargs.setdefault('deprecation_reason', field.deprecation_reason)
        return graphene.Field(**kwargs)