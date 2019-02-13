"""Graphene types.  """
from functools import partial

import graphene
import graphene_django
from graphene_django.filter import DjangoFilterConnectionField
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


class ModelFilterConnectionField(ModelConnectionField):
    """`DjangoFilterConnectionField` for model.  """

    args = DjangoFilterConnectionField.args
    filterset_class = DjangoFilterConnectionField.filterset_class
    filtering_args = DjangoFilterConnectionField.filtering_args
    merge_querysets = DjangoFilterConnectionField.merge_querysets
    get_resolver = DjangoFilterConnectionField.get_resolver

    def __init__(self, model,
                 fields=None,
                 extra_filter_meta=None,
                 filterset_class=None,
                 **kwargs):
        kwargs.setdefault('description',
                          (model.__doc__
                           or f'Filterable connection for database model: {model.__name__}'))
        self._node_filterset_class = None

        self._fields = fields
        self._provided_filterset_class = filterset_class
        self._filterset_class = None
        self._extra_filter_meta = extra_filter_meta
        self._base_args = None
        super().__init__(model, **kwargs)

    @property
    def _provided_filterset_class(self):
        if self._node_filterset_class is None:
            meta = getattr(self.node_type, '_meta')
            self._node_filterset_class = getattr(meta, 'filterset_class', None)
        return self._node_filterset_class

    @_provided_filterset_class.setter
    def _provided_filterset_class(self, value):
        self._node_filterset_class = value

    @classmethod
    def connection_resolver(
            cls,
            resolver,
            connection,
            default_manager,
            max_limit,
            enforce_first_or_last,
            filterset_class,
            filtering_args,
            root,
            info,
            **kwargs):
        # pylint: disable=R0913,W0221
        filter_kwargs = {k: v for k,
                         v in kwargs.items()
                         if k in filtering_args}
        queryset = filterset_class(
            data=filter_kwargs,
            queryset=default_manager.get_queryset(),
            request=info.context,).qs

        return super().connection_resolver(
            resolver,
            connection,
            queryset,
            max_limit,
            enforce_first_or_last,
            root,
            info,
            **kwargs)
