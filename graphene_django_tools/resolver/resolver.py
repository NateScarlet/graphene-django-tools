# -*- coding=UTF-8 -*-
"""Apollo-like resolver.  """

from __future__ import annotations
import typing

import django
import graphene
import graphql

from . import schema as schema_
from . import typedef


class Resolver:
    """Apollo-like schema field resolver.  """

    # Resolver definitions.
    schema: typing.Optional[typing.MutableMapping] = None

    # Data that avaliable inside `resolve`.
    parent: typing.Any
    info: graphql.execution.base.ResolveInfo
    context: django.core.handlers.wsgi.WSGIRequest

    _field: typing.Optional[graphene.Field] = None
    _type: typing.Optional[graphene.Scalar | graphene.ObjectType] = None

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
        # pylint:disable=unused-argument
        return None

    def validate(self, value) -> bool:
        """Test whether value is match resolver schema type.

        Args:
            value (typing.Any): Value to validate.

        Returns:
            bool: whether value match schema type.
        """
        # pylint:disable=unused-argument
        return True

    @classmethod
    def as_type(
            cls,
            namespace: str = None
    ) -> typing.Union[graphene.Scalar, graphene.ObjectType]:
        """Convert resolver as graphene type.

        Args:
            namespace (str, optional): [description]. Defaults to None.
                namespace for auto naming, use class name when value is None.

        Returns:
            typing.Union[graphene.Scalar,graphene.ObjectType]:
        """

        if cls._type:
            return cls._type
        namespace = namespace or cls.__name__
        ret = typedef.build_type(
            namespace=namespace,
            schema=cls.schema,
            mapping_bases=(graphene.ObjectType,),
        )

        if (isinstance(ret, type)
                and issubclass(ret, graphene.ObjectType)):
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

        if not cls.schema:
            raise NotImplementedError(
                f'Resolver schema is not defined: {cls.__name__}')
        schema = schema_.FieldDefinition.parse(cls.schema)
        if cls._field:
            return cls._field

        _type = cls.as_type(namespace=schema.name or cls.__name__)
        args_type = typedef.build_args_type(
            cls.__name__,
            schema.args,
        ) if schema.args else None

        def resolver(parent, info, **kwargs):
            return cls(parent=parent, info=info).resolve(**kwargs)

        cls._field = schema.mount_as_field(
            type=_type,
            args=args_type,
            resolver=resolver,
        )
        return cls._field
