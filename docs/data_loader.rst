Data loader integration
==========================================

Use ``Resolver.get_loader`` method get loader for given django model.
It takes a django model type as argument, and returns corresponding ``promise.DataLoader``.
Data loader is cached in request scope with `_django_model_loader_cache` key.

Use ``Resolver.resolve_gid`` method to resolve model object from graphene global node id.
It returns a promise and prime object to data loader cache on resolve.
