"""Graphene types.  """
from datetime import timedelta

import graphene
import graphene_django
import graphene_django.filter
import isodate
from graphql.language import ast

from . import core


class ModelField(graphene.Field):
    """`Field` for model.

    Use `create_nodemodel` first if you want customize the node.
    """

    def __init__(self, model, **kwargs):
        kwargs.setdefault('description',
                          (model.__doc__
                           or f'Node for database model: {model.__name__}'))
        super().__init__(lambda: core.get_modelnode(model), **kwargs)


class ModelListField(graphene.List):
    """`List` field for model.

    Use `create_nodemodel` first if you want customize the node.
    """

    def __init__(self, model, **kwargs):
        kwargs.setdefault('description',
                          (model.__doc__
                           or f'Node list for database model: {model.__name__}'))
        super().__init__(lambda: core.get_modelnode(model), **kwargs)


class CustomConnectionResolveMixin:
    """Print traceback when encountered a error"""

    @classmethod
    def connection_resolver(cls, *args, **kwargs):
        try:
            return super().connection_resolver(*args, **kwargs)
        except:
            core.handle_resolve_error()
            raise


class ModelConnectionField(CustomConnectionResolveMixin, graphene_django.DjangoConnectionField):
    """`DjangoConnectionField` for model.

    Use `create_nodemodel` first if you want customize the node.
    """

    def __init__(self, model, **kwargs):
        kwargs.setdefault('description',
                          (model.__doc__
                           or f'Connection for database model: {model.__name__}'))
        super().__init__(lambda: core.get_modelnode(model), **kwargs)


class ModelFilterConnectionField(CustomConnectionResolveMixin,
                                 graphene_django.filter.DjangoFilterConnectionField):
    """`DjangoFilterConnectionField` for model.  """

    def __init__(self, model, **kwargs):
        kwargs.setdefault('description',
                          (model.__doc__
                           or f'Fitlerable connection for database model: {model.__name__}'))
        self._node_filterset_class = None
        super().__init__(lambda: core.get_modelnode(model), **kwargs)

    @property
    def _provided_filterset_class(self):
        if self._node_filterset_class is None:
            meta = getattr(self.node_type, '_meta')
            self._node_filterset_class = getattr(meta, 'filterset_class', None)
        return self._node_filterset_class

    @_provided_filterset_class.setter
    def _provided_filterset_class(self, value):
        self._node_filterset_class = value


class Duration(graphene.Scalar):
    """Duration in ISO-8601 format.  """

    @staticmethod
    def serialize(duration: timedelta):
        """Serialize python object.

        Args:
            duration (timedelta): Duration

        Returns:
            str
        """

        return isodate.duration_isoformat(duration)

    @classmethod
    def parse_literal(cls, node):
        """Parse ast node.

        Args:
            node: AST node

        Returns:
            timedelta | None
        """

        if isinstance(node, ast.StringValue):
            return cls.parse_value(node.value)
        return None

    @staticmethod
    def parse_value(value):
        """Parse str to python object.

        Args:
            value (str): Value

        Returns:
            timedelta | None
        """

        try:
            return isodate.parse_duration(value)
        except ValueError:
            return None


class CountableConnection(graphene.relay.Connection):
    """Extended connection with total count.  """

    class Meta:
        abstract = True

    total = graphene.Int()

    @staticmethod
    def resolve_total(root, _info):
        return root.length


class ModelNodeOptions(graphene_django.types.DjangoObjectTypeOptions):
    """Extended DjangoObjectTypeOptions for `ModelNode`.  """

    filterset_class = None


class ModelNode(graphene_django.DjangoObjectType):
    class Meta:
        abstract = True

    @classmethod
    def __init_subclass_with_meta__(
            cls,
            filterset_class=None,
            **options):
        # pylint: disable=W0221
        _meta = options.get('_meta', ModelNodeOptions(cls))
        _meta.filterset_class = filterset_class
        options['_meta'] = _meta
        super().__init_subclass_with_meta__(**options)
