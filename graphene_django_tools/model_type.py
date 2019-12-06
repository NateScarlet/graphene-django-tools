"""handle relationship between django model and graphene type. """

from __future__ import annotations
from functools import lru_cache
import typing

import django.db.models as djm

import graphene_django_tools as gdtools

from . import core

if typing.TYPE_CHECKING:
    from django.db.models import Model  # type: ignore


MODEL_TYPENAME_REGISTRY: typing.Dict[typing.Type[Model], str] = {}


def get_typename_for_model(model: typing.Type[Model]) -> str:
    """Get graphql typename for given model.

    Args:
        model (typing.Type[Model]): Django model

    Returns:
        str: Type name used in graphql.
    """
    if model not in MODEL_TYPENAME_REGISTRY:
        MODEL_TYPENAME_REGISTRY[model] = core.get_modelnode(
            model, is_autocreate=False)._meta.name
    return MODEL_TYPENAME_REGISTRY[model]


def get_model_typename(model: typing.Type[Model]) -> str:
    import warnings
    warnings.warn(
        "`get_model_typename` renamed to `get_typename_for_model`.",
        DeprecationWarning
    )
    return get_typename_for_model(model)


@lru_cache()
def get_models_for_typename(v: str) -> typing.List[typing.Type[djm.Model]]:
    """Get models for typename.

    Args:
        v (str): typename

    Returns:
        typing.List[djm.Model]: list of models that registered for this typename.
    """

    ret = []
    for model, typename in gdtools.MODEL_TYPENAME_REGISTRY.items():
        if typename == v:
            ret.append(model)
    return ret
