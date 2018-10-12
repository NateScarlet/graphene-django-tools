"""Graphene types.  """
import graphene
import graphene_django
import graphene_django.filter

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


class ModelConnectionField(graphene_django.DjangoConnectionField):
    """`DjangoConnectionField` for model.

    Use `create_nodemodel` first if you want customize the node.
    """

    def __init__(self, model, **kwargs):
        kwargs.setdefault('description',
                          (model.__doc__
                           or f'Connection for database model: {model.__name__}'))
        super().__init__(core.get_modelnode(model), **kwargs)


class ModelFilterConnectionField(graphene_django.filter.DjangoFilterConnectionField):
    """`DjangoFilterConnectionField` for model.

    Use `create_nodemodel` first if you want customize the node.
    """

    def __init__(self, model, **kwargs):
        kwargs.setdefault('description',
                          (model.__doc__
                           or f'Fitlerable connection for database model: {model.__name__}'))
        super().__init__(core.get_modelnode(model), **kwargs)
