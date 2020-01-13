Data loader integration
==========================================

Enable by add `'graphene_django_tools.dataloader.middleware.DataLoaderMiddleware'` to your django settings `GRAPHENE['MIDDLEWARE']`

When enabled, you will have `get_data_loader` method on your resolve context object.
It takes a django model type as argument, and returns corresponding `promise.DataLoader`.
Data loader is cached in request scope with `data_loader_cache` key.
