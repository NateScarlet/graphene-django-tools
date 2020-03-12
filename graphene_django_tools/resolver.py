"""Enhanced graphene resolver for django.  """

import typing

import graphene_resolver

from . import dataloader, model_type
from .global_id import GlobalID

if typing.TYPE_CHECKING:
    from promise import Promise
    from promise.dataloader import DataLoader


class Resolver(graphene_resolver.Resolver, abstract=True):
    """Enhanced graphene-resolver resolver.  

    schema: schema definition
    model: django model
    """

    _data_loader_cache_attname = '_django_model_loader_cache'
    model: typing.Optional[typing.Type] = None

    def __init_subclass__(cls, **kwargs):
        # pylint: disable=arguments-differ
        super().__init_subclass__(**kwargs)
        if cls.model:
            model_type.REGISTRY[cls.model] = cls._schema.name

    def get_loader(self, model) -> 'DataLoader':
        """Get dataloader for model.
        for same request, will always returns same dataloader object.

        Returns:
            DataLoader: Dataloader for given model
        """

        ctx = self.context
        attname = self._data_loader_cache_attname
        if not hasattr(ctx, attname):
            setattr(ctx, attname, {})
        cache = getattr(ctx, attname)
        if model not in cache:
            cache[model] = dataloader.get_for_model(model)
        return cache[model]

    def resolve_gid(self, v) -> 'Promise':
        """Resolve global id to a model object promise,
        using dataloader.

        Returns:
            Promise: resolve to model object.
        """

        gid = GlobalID.cast(v)
        model = model_type.get_model(gid.type)
        loader = self.get_loader(model)
        if isinstance(v, model):
            loader.prime(gid.value, v)
        return loader.load(gid.value)

    def get_node(self, id_):
        return self.resolve_gid(id_)

    def validate(self, value):
        if not self.model:
            return super().validate(value)
        return isinstance(value, self.model)
