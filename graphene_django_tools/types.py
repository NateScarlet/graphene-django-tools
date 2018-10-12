"""Graphene types.  """
import graphene

from . import core


class ModelField(graphene.Field):
    """Field for mapping a model.

    User create_nodemodel first if you want custom the field.
    """

    def __init__(self, model, **kwargs):
        kwargs.setdefault('description',
                          model.__doc__ or f'Node for database model: {model.__name__}')
        super().__init__(core.get_modelnode(model), **kwargs)
