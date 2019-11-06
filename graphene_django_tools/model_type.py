"""handle relationship between django model and graphene type. """

from __future__ import annotations
from . import core

import typing

if typing.TYPE_CHECKING:
    from django.db.models import Model  # type: ignore


MODEL_TYPENAME_REGISTRY: typing.Dict[typing.Type[Model], str] = {}


def get_model_typename(model: typing.Type[Model]) -> str:
    """Get graphql typename for given model.

    Args:
        model (typing.Type[Model]): Django model

    Returns:
        str: Type name used in graphql.
    """
    if model in MODEL_TYPENAME_REGISTRY:
        return MODEL_TYPENAME_REGISTRY[model]
    return core.get_modelnode(model, is_autocreate=False)._meta.name
