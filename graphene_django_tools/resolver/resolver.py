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

    def __init__(self,
                 parent: typing.Any,
                 info: graphql.execution.base.ResolveInfo):
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
        namespace = schema.name or cls.__name__
        if namespace in RESOLVER_REGISTRY:
            return RESOLVER_REGISTRY[namespace]

        _type = typedef.build_type(
            namespace=namespace,
            schema=cls.schema,
            mapping_bases=(graphene.ObjectType,),
        )
        args_type = typedef.build_args_type(
            cls.__name__,
            schema.args,
        ) if schema.args else None

        def resolver(parent, info, **kwargs):
            return cls(parent=parent, info=info).resolve(**kwargs)

        RESOLVER_REGISTRY[namespace] = schema.mount_as_field(
            type=_type,
            args=args_type,
            resolver=resolver,
            required=False,
        )
        return RESOLVER_REGISTRY[namespace]


RESOLVER_REGISTRY: typing.Dict[str, Resolver] = {}
