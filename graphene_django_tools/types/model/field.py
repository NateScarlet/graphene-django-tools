"""Graphene types.  """
from functools import partial

import graphene
import graphene_django
from promise import Promise

from ... import core
from ..mixin import CustomConnectionResolveMixin


class ModelField(graphene.Field):
    """`Field` for model.

    Use `create_nodemodel` first if you want customize the node.
    """

    def __init__(self, model, **kwargs):
        kwargs.setdefault('description',
                          (model.__doc__
                           or f'Node for database model: {model.__name__}'))
        super().__init__(lambda: core.get_modelnode(model), **kwargs)
        self.model = model


class ModelListField(graphene_django.fields.DjangoListField):
    """`List` field for model.

    Use `create_nodemodel` first if you want customize the node.
    """

    def __init__(self, model, **kwargs):
        kwargs.setdefault('description',
                          (model.__doc__
                           or f'Node list for database model: {model.__name__}'))
        super().__init__(lambda: core.get_modelnode(model), **kwargs)


class ModelConnectionField(CustomConnectionResolveMixin, graphene_django.DjangoConnectionField):
    """`DjangoConnectionField` for model.

    Use `create_nodemodel` first if you want customize the node.
    """

    def __init__(self, model, **kwargs):
        kwargs.setdefault('description',
                          (model.__doc__
                           or f'Connection for database model: {model.__name__}'))
        super().__init__(lambda: core.get_modelnode(model), **kwargs)

    @classmethod
    def connection_resolver(
            cls,
            resolver,
            connection,
            default_manager,
            max_limit,
            enforce_first_or_last,
            root,
            info,
            **kwargs):
        # pylint: disable=R0913,W0221

        first = kwargs.get("first")
        last = kwargs.get("last")
        if not (first is None or first > 0):
            raise ValueError(
                f'`first` argument must be positive, got `{first}`')
        if not (last is None or last > 0):
            raise ValueError(
                f'`last` argument must be positive, got `{last}`')
        if enforce_first_or_last and not (first or last):
            raise ValueError(
                f"You must provide a `first` or `last` value "
                f"to properly paginate the `{info.field_name}` connection.")

        if not max_limit:
            pass
        elif first is None and last is None:
            kwargs['first'] = max_limit
        else:
            count = min(i for i in (first, last) if i)
            if count > max_limit:
                raise ValueError(f"Requesting {count} records "
                                 f"on the `{info.field_name}` connection "
                                 f"exceeds the limit of {max_limit} records.")

        iterable = resolver(root, info, **kwargs)
        on_resolve = partial(cls.resolve_connection,
                             connection, default_manager, kwargs)

        if Promise.is_thenable(iterable):
            return Promise.resolve(iterable).then(on_resolve)

        return on_resolve(iterable)
