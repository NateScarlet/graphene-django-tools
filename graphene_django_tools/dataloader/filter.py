"""Graphql types for data loader.  """

from functools import partial

from ..types import ModelFilterConnectionField
from .types import DataLoaderModelConnectionMixin, get_resolver_with_info


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
