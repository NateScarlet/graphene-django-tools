"""handle relationship between django model and graphene type. """

from __future__ import annotations
from functools import lru_cache
import typing

import django.db.models as djm


if typing.TYPE_CHECKING:
    from django.db.models import Model  # type: ignore


REGISTRY: typing.Dict[typing.Type[Model], str] = {}


@lru_cache()
def get_models(v: str) -> typing.List[typing.Type[djm.Model]]:
    """Get models for typename.

    Args:
        v (str): typename

    Returns:
        typing.List[djm.Model]: list of models that registered for this typename.
    """

    ret = []
    for model, typename in REGISTRY.items():
        if typename == v:
            ret.append(model)
    return ret
