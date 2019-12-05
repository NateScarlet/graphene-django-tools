"""Graphene types.  """

from graphene_django.filter import DjangoFilterConnectionField

from .field import ModelConnectionField


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
