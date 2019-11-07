# -*- coding=UTF-8 -*-
"""Mongoose-like schema.  """
# pylint:disable=unused-import

from __future__ import annotations

import dataclasses
import typing

import django.db.models
import graphene
import graphene_django.converter
import graphene_django.registry

from .. import texttools
from . import typedef


@dataclasses.dataclass
class FieldDefinition:
    """A mongoose-like schema for resolver field.  """

    # Options:
    args: typing.Mapping
    type: typing.Type
    required: bool
    name: str
    interfaces: typing.Tuple[typing.Type[graphene.Interface], ...]
    description: typing.Optional[str]
    deprecation_reason: typing.Optional[str]
    resolver: typing.Optional[typing.Callable]
    default: typing.Any

    # Parse results:
    child_definition: typing.Any

    @classmethod
    def parse(cls, v: typing.Any, *, default: typing.Dict = None) -> FieldDefinition:
        """Parse a mongoose like schema

        Args:
            v (typing.Any): schema item

        Returns:
            SchemaDefinition: Parsing result
        """
        from . import resolver

        assert v is not None, 'schema is None'
        config = default or {}
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
        if 'name' not in config:
            raise ValueError(f'Not specified field name in: {v}')
        # Convert args
        config.setdefault('args', {})
        if config['args']:
            config['args'] = {
                k: (cls
                    .parse(
                        v,
                        default={
                            'name': texttools.camel_case(f'{config["name"]}_{k}')
                        })
                    .mount(as_=graphene.Argument))
                for k, v in config['args'].items()
            }
        # Convert interfaces
        config.setdefault('interfaces', ())
        config['interfaces'] = tuple(
            i.as_interface() if (isinstance(i, type) and issubclass(i, resolver.Resolver)) else i
            for i in config['interfaces']
        )

        if isinstance(type_def, django.db.models.Field):
            config['type'] = graphene_django.converter.convert_django_field_with_choices(
                type_def,
                registry=graphene_django.registry.get_global_registry()).__class__
        elif isinstance(type_def, type) and issubclass(type_def, resolver.Resolver):
            _resolver: typing.Type[resolver.Resolver] = type_def
            # merge schema
            config['name'] = _resolver._schema.name
            config['type'] = _resolver.as_type()
            config['args'].update(**_resolver._schema.args)
            config['interfaces'] += _resolver._schema.interfaces
            config.setdefault('required', _resolver._schema.required)

            _parent_resolver = config.get('resolver')

            def resolve_fn(parent, info, **kwargs):
                if _parent_resolver:
                    parent = _parent_resolver(parent, info, **kwargs)
                return _resolver._schema.resolver(parent, info, **kwargs)
            config.setdefault('resolver', resolve_fn)
            config.setdefault('description', _resolver._schema.description)
            config.setdefault('deprecation_reason',
                              _resolver._schema.deprecation_reason)
            child_definition = _resolver._schema.child_definition
        elif isinstance(type_def, str):
            if type_def[-1] == '!':
                config.setdefault('required', True)
                type_def = type_def[:-1]
            config['type'] = type_def
        elif isinstance(type_def, typing.Mapping):
            config['type'] = dict
            child_definition = type_def
        elif isinstance(type_def, typing.Iterable):
            config['type'] = list
            assert len(type_def) == 1, type_def
            child_definition = type_def[0]
        else:
            config['type'] = type_def

        config.setdefault('required', False)
        config.setdefault('description', None)
        config.setdefault('deprecation_reason', None)
        config.setdefault('resolver', None)
        config.setdefault('default', None)

        return cls(
            type=config['type'],
            required=config['required'],
            name=config['name'],
            description=config['description'],
            deprecation_reason=config['deprecation_reason'],
            args=config['args'],
            interfaces=config['interfaces'],
            resolver=config['resolver'],
            default=config['default'],
            child_definition=child_definition,
        )

    def _get_options(self, target: typing.Type):
        allowed_options = ()
        if not isinstance(target, type):
            pass

        allowed_options_by_type = [
            (graphene.Argument,
             ('required', 'default_value', 'description', )),
            (graphene.Field,
             ('args', 'resolver', 'required', 'default_value',
              'description', 'deprecation_reason', )),
            (graphene.InputField,
             ('required', 'default_value', 'description', 'deprecation_reason',)),
        ]
        for classinfo, options in allowed_options_by_type:
            if issubclass(target, classinfo):
                allowed_options += options

        options = dict(
            name=self.name,
            required=self.required,
            description=self.description,
            deprecation_reason=self.deprecation_reason,
            args=self.args,
            resolver=self.resolver,
            default_value=self.default,
        )

        return {k: v for k, v in options.items() if k in allowed_options}

    def as_type(
            self,
            *,
            mapping_bases: typing.Tuple[typing.Type] = (graphene.ObjectType,),
            registry=None
    ) -> graphene.types.unmountedtype.UnmountedType:
        """Convert schema to graphene unmmounted type instance with options set.

        Args:
            is_input (bool, optional): Whether is input field. Defaults to False.
            registry (typing.Dict, optional): Graphene type registry. Defaults to None.

        Returns:
            graphene.types.unmountedtype.UnmountedType: result
        """
        registry = registry or typedef.GRAPHENE_TYPE_REGISTRY

        namespace = self.name
        is_input = graphene.InputObjectType in mapping_bases

        options = self._get_options(
            graphene.Argument if is_input else graphene.Field)
        ret = None
        # Mapping
        if self.type is dict:
            assert self.child_definition
            _type: typing.Type = type(
                namespace,
                mapping_bases,
                {
                    **{
                        k: (self.parse(
                            v,
                            default={
                                'name': texttools.camel_case(f'{namespace}_{k}')}
                        ).mount(as_=graphene.InputField if is_input else graphene.Field))
                        for k, v in self.child_definition.items()
                    },
                    **dict(
                        Meta=dict(
                            name=self.name,
                            interfaces=self.interfaces,
                            description=self.description,
                        )
                    )
                })
            registry[namespace] = _type
            ret = _type
        # Iterable
        elif self.type is list:
            assert self.child_definition
            _item_schema = self.parse(
                self.child_definition,
                default={'name': namespace}
            )
            _item_type = _item_schema.as_type(mapping_bases=mapping_bases)
            if _item_schema.required:
                # `required` option for list item not work,
                # so non-null structure is required.
                _item_type = graphene.NonNull(_item_type)
            ret = graphene.List(
                _item_type,
                **options
            )
        # Unmounted type.
        elif (isinstance(self.type, type)
              and issubclass(self.type, graphene.types.unmountedtype.UnmountedType)):
            ret = self.type(**options)
        # Dynamic
        elif isinstance(self.type, str):
            ret = typedef.dynamic_type(self.type)
        # As-is
        else:
            ret = self.type
        return ret

    def mount(
            self,
            *,
            as_: typing.Type,
            type_: graphene.types.unmountedtype.UnmountedType = None,
            registry=None
    ):
        """Mount schema as a graphene mounted type instance.

        Args:
            as_ (typing.Type): Target type
            type_ (graphene.types.unmountedtype.UnmountedType, optional):
                Override unmmounted type. Defaults to None.
            registry (typing.Mapping, optional): Graphene type registry. Defaults to None.

        Returns:
            Mounted type instance.
        """

        is_input = (
            isinstance(as_, type)
            and issubclass(
                as_,
                (graphene.Argument, graphene.InputField, graphene.InputObjectType)))
        mapping_bases = (graphene.InputObjectType,
                         ) if is_input else (graphene.ObjectType,)
        type_ = type_ or self.as_type(
            mapping_bases=mapping_bases, registry=registry)

        if isinstance(type_, graphene.types.unmountedtype.UnmountedType):
            return type_.mount_as(as_)
        return as_(type=type_, **self._get_options(as_))
