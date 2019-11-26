"""Graphql middleware for data loader.  """

import logging

from promise import Promise
from promise.dataloader import DataLoader

import graphene_django_tools as gdtools

LOGGER = logging.getLogger(__name__)


def get_model_batch_load_fn(model):
    """Create batch load function for model.  """

    def batch_load_fn(keys):
        keys = [int(i) for i in keys]
        LOGGER.debug('load: %s: %s', model, keys)
        result = model.objects.in_bulk(keys)
        return Promise.resolve([result[i] for i in keys])

    return batch_load_fn


def get_model_data_loader(model):
    """Create dataloader for model.  """

    return DataLoader(get_model_batch_load_fn(model))


class DataLoaderMiddleware:
    """Middleware to add `context.get_dataloader` method.  """

    cache_attrname = 'data_loader_cache'

    def resolve(self, resolve_next, parent, info: gdtools.ResolveInfo, **kwargs):
        """Graphene middleware resolve method.  """

        def get_data_loader(model):
            attrname = self.cache_attrname
            if not hasattr(info.context, attrname):
                setattr(info.context, attrname, {})
            cache = getattr(info.context, attrname)
            if model not in cache:
                cache[model] = get_model_data_loader(model)
            return cache[model]

        info.context.get_data_loader = get_data_loader
        return resolve_next(parent, info, **kwargs)
