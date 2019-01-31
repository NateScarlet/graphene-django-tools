"""Graphql types for data loader.  """

from functools import partial

import graphene
from django.db import models
from graphene_django.utils import maybe_queryset
from graphql.execution.base import ResolveInfo
from graphql_relay.connection.arrayconnection import connection_from_list_slice
from promise import Promise

from ..types import ModelFilterConnectionField


class DataLoaderModelFilterConnectionField(ModelFilterConnectionField):
    """Model filter connection field with data loader support.  """

    @classmethod
    def resolve_connection(cls, connection, default_manager, args, iterable):
        def construct_connection(iterable):
            iterable = list(iterable)
            _len = len(iterable)
            ret = connection_from_list_slice(
                iterable,
                args,
                slice_start=0,
                list_length=_len,
                list_slice_length=_len,
                connection_type=connection,
                edge_type=connection.Edge,
                pageinfo_type=graphene.relay.PageInfo,
            )
            ret.iterable = iterable
            ret.length = _len
            return ret

        info = getattr(iterable, 'info', None)
        if iterable is None:
            iterable = default_manager
        iterable = maybe_queryset(iterable)

        if isinstance(iterable, models.QuerySet) and iterable is not default_manager:
            default_queryset = maybe_queryset(default_manager)
            iterable = cls.merge_querysets(default_queryset, iterable)
        if info:
            iterable = (info
                        .context
                        .get_data_loader(default_manager
                                         .model)
                        .load_many(iterable
                                   .values_list('pk', flat=True)))
        if Promise.is_thenable(iterable):
            return Promise.resolve(iterable).then(construct_connection)
        return construct_connection(iterable)

    def get_resolver(self, parent_resolver):
        def resolver(parent, info: ResolveInfo, **kwargs):
            ret = parent_resolver(parent, info, **kwargs)
            try:
                ret.info = info
            except AttributeError:
                # `ret` may be None
                pass
            return ret

        return partial(
            self.connection_resolver,
            resolver,
            self.type,
            self.get_manager(),
            self.max_limit,
            self.enforce_first_or_last,
            self.filterset_class,
            self.filtering_args
        )
