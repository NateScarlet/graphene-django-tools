"""handle relationship between django model and graphene type. """

from functools import lru_cache
import typing

import django.contrib.contenttypes.models as ctm
import django.db.models as djm


if typing.TYPE_CHECKING:
    from django.db.models import Model  # type: ignore


REGISTRY: typing.Dict[typing.Type['Model'], str] = {}


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


def get_content_type(typename: str) -> ctm.ContentType:
    """Get django.contrib.contenttype for typename.

    Args:
        typename (str): Graphql typename.

    Raises:
        ValueError: When not exact one matched model for given typename.

    Returns:
        ctm.ContentType: ContentType object for given typename.
    """

    models = get_models(typename)
    if len(models) != 1:
        raise ValueError(
            f"Can not determinate model from typename: typename={typename}")
    return ctm.ContentType.objects.get_for_model(models[0])
