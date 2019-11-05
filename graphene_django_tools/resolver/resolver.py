# -*- coding=UTF-8 -*-
"""Apollo-like resolver.  """

from __future__ import annotations
import typing

import django
import graphene
import graphql

from . import schema as schema_


class Resolver:
    """Apollo-like schema field resolver.  """

    # Resolver definitions.
    schema: typing.Optional[typing.MutableMapping] = None

    # Data that avaliable inside `resolve`.
    parent: typing.Any
    info: graphql.execution.base.ResolveInfo
    context: django.core.handlers.wsgi.WSGIRequest

    _field: typing.Optional[graphene.Field] = None
    _schema: schema_.FieldDefinition
    _type: typing.Optional[graphene.Scalar | graphene.ObjectType] = None
    _as_interface: typing.Optional[typing.Type[graphene.Interface]] = None

    def __init_subclass__(cls):
        cls._parse_schema(default={'name': cls.__name__})
        cls.as_type()

    def __init__(
            self,
            *,
            info: graphql.execution.base.ResolveInfo,
            parent: typing.Any = None,
    ):
        self.parent = parent
        self.info = info
        self.context = info.context

    def resolve(self, **kwargs):
        """Resolve the field.  """
        # pylint:disable=unused-argument

        field_name = self.info.field_name
        if isinstance(self.parent, typing.Mapping) and field_name in self.parent:
            return self.parent[field_name]
        elif hasattr(self.parent, field_name):
            return getattr(self.parent, field_name)
        raise NotImplementedError(
            f'`{self.__class__.__name__}.resolve` is not implemented.')

    def get_node(self, id_: str):
        """Get node value from id.

        Args:
            id_ (str): Node id.

        Returns:
            typing.Any: Corresponding node value.
        """
        # pylint:disable=unused-argument,no-self-use
        return None

    def validate(self, value) -> bool:
        """Test whether value is match resolver schema type.

        Args:
            value (typing.Any): Value to validate.

        Returns:
            bool: whether value match schema type.
        """
        # pylint:disable=unused-argument,no-self-use
        return True

    @classmethod
    def _parse_schema(cls, *, default: typing.Dict):
        if not cls.schema:
            raise NotImplementedError(
                f'Resolver schema is not defined: {cls.__name__}')

        def resolve_fn(parent, info, **kwargs):
            return cls(parent=parent, info=info).resolve(**kwargs)
        cls._schema = schema_.FieldDefinition.parse(
            cls.schema,
            default={**default, 'resolver': resolve_fn}
        )
        return cls._schema

    @classmethod
    def as_type(
            cls,
    ) -> graphene.types.unmountedtype.UnmountedType:
        """Convert resolver as graphene type.

        Args:
            namespace (str, optional): [description]. Defaults to None.
                namespace for auto naming, use class name when value is None.

        Returns:
            graphene.types.unmountedtype.UnmountedType:
        """

        if cls._type:
            return cls._type

        ret = cls._schema.as_type()

        def get_node(info, id_):
            return cls(info=info).get_node(id_)
        ret.get_node = get_node

        def is_type_of(value, info):
            return cls(info=info).validate(value)
        ret.is_type_of = is_type_of

        cls._type = ret
        return ret

    @classmethod
    def as_field(cls) -> graphene.Field:
        """Convert resolver as a graphene field.

        Returns:
            graphene.Field: Converted field.
        """

        if cls._field:
            return cls._field

        cls._field = cls._schema.mount(type_=cls.as_type(), as_=graphene.Field)
        return cls._field

    @classmethod
    def as_interface(cls) -> typing.Type[graphene.Interface]:
        """Convert resolver schema as interface

        Raises:
            ValueError: Can not convert to interface.

        Returns:
            typing.Type[graphene.Interface]: Convert result, will cache on class.
        """
        if cls._schema.type is not dict:
            raise ValueError(
                f'Schema can not use as interface, should be mapping: {cls.__name__}')

        if cls._as_interface:
            return cls._as_interface
        cls._as_interface = cls._schema.as_type(
            mapping_bases=(graphene.Interface,))
        return cls._as_interface
