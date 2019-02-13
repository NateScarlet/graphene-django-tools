"""Graphql types for data loader.  """

from functools import partial

import graphene
from django.db import models
from graphene_django.utils import maybe_queryset
from graphql.execution.base import ResolveInfo
from graphql_relay.connection.arrayconnection import connection_from_list_slice
from promise import Promise

from ..types import (ModelConnectionField, ModelField,
                     ModelFilterConnectionField, ModelListField)


class DataLoaderModelConnectionMixin:
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
        if info and hasattr(info.context, 'get_data_loader'):
            iterable = (info
                        .context
                        .get_data_loader(default_manager
                                         .model)
                        .load_many(iterable
                                   .values_list('pk', flat=True)))
        if Promise.is_thenable(iterable):
            return Promise.resolve(iterable).then(construct_connection)
        return construct_connection(iterable)


def get_resolver_with_info(parent_resolver):

    def resolver(parent, info: ResolveInfo, **kwargs):
        ret = parent_resolver(parent, info, **kwargs)
        try:
            ret.info = info
        except AttributeError:
            # `ret` may be None
            pass
        return ret
    return resolver


class DataLoaderModelFilterConnectionField(DataLoaderModelConnectionMixin, ModelFilterConnectionField):
    """Model filter connection field with data loader support.  """

    def get_resolver(self, parent_resolver):

        return partial(
            self.connection_resolver,
            get_resolver_with_info(parent_resolver),
            self.type,
            self.get_manager(),
            self.max_limit,
            self.enforce_first_or_last,
            self.filterset_class,
            self.filtering_args
        )


class DataLoaderModelConnectionField(DataLoaderModelConnectionMixin, ModelConnectionField):
    """Model connection field with data loader support.  """

    def get_resolver(self, parent_resolver):
        return partial(
            self.connection_resolver,
            get_resolver_with_info(parent_resolver),
            self.type,
            self.get_manager(),
            self.max_limit,
            self.enforce_first_or_last,
        )


class DataLoaderModelListField(ModelListField):
    """Model list field with data loader support.  """

    def get_resolver(self, parent_resolver):
        return partial(self.resolve, parent_resolver)

    def resolve(self, resolver, root, info: ResolveInfo, **kwargs):
        iterable = maybe_queryset(resolver(root, info, **kwargs))
        if isinstance(iterable, models.QuerySet) and hasattr(info.context, 'get_data_loader'):
            iterable = (info
                        .context
                        .get_data_loader(self.model)
                        .load_many(iterable
                                   .values_list('pk', flat=True)))
        return iterable


class DataLoaderModelField(ModelField):
    """Model field with data loader support.  """

    def get_resolver(self, parent_resolver):
        return partial(self.resolve, parent_resolver)

    def resolve(self, resolver, root, info: ResolveInfo, **kwargs):
        ret = resolver(root, info, **kwargs)
        if isinstance(ret, self.model) and hasattr(info.context, 'get_data_loader'):
            ret = (info
                   .context
                   .get_data_loader(self.model)
                   .load(ret.pk))
        return ret
