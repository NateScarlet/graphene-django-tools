"""Data loader for django model.  """

import logging

from promise import Promise
from promise.dataloader import DataLoader

LOGGER = logging.getLogger(__name__)


def _get_model_batch_load_fn(model):
    """Create batch load function for model.  """

    def batch_load_fn(keys):
        keys = [int(i) for i in keys]
        LOGGER.debug('load: %s: %s', model, keys)
        result = model.objects.in_bulk(keys)
        return Promise.resolve([result[i] for i in keys])

    return batch_load_fn


def get_for_model(model):
    """Create dataloader for model.  """

    return DataLoader(_get_model_batch_load_fn(model))
