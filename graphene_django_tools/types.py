"""Graphene types.  """
import graphene
import graphene_django
import graphene_django.filter
from graphql import GraphQLError

from . import core


class ModelField(graphene.Field):
    """`Field` for model.

    Use `create_nodemodel` first if you want customize the node.
    """

    def __init__(self, model, **kwargs):
        kwargs.setdefault('description',
                          (model.__doc__
                           or f'Node for database model: {model.__name__}'))
        super().__init__(core.get_modelnode(model), **kwargs)


class ModelListField(graphene.List):
    """`List` field for model.

    Use `create_nodemodel` first if you want customize the node.
    """

    def __init__(self, model, **kwargs):
        kwargs.setdefault('description',
                          (model.__doc__
                           or f'Node list for database model: {model.__name__}'))
        super().__init__(core.get_modelnode(model), **kwargs)


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
        super().__init__(core.get_modelnode(model), **kwargs)


class ModelFilterConnectionField(CustomConnectionResolveMixin, graphene_django.filter.DjangoFilterConnectionField):
    """`DjangoFilterConnectionField` for model.

    Use `create_nodemodel` first if you want customize the node.
    """

    def __init__(self, model, **kwargs):
        kwargs.setdefault('description',
                          (model.__doc__
                           or f'Fitlerable connection for database model: {model.__name__}'))
        super().__init__(core.get_modelnode(model), **kwargs)
