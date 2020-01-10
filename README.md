# Graphene django tools

[![build status](https://github.com/NateScarlet/graphene-django-tools/workflows/Python%20package/badge.svg)](https://github.com/NateScarlet/graphene-django-tools/actions)
[![version](https://img.shields.io/pypi/v/graphene-django-tools)](https://pypi.org/project/graphene-django-tools/)
![python version](https://img.shields.io/pypi/pyversions/graphene-django-tools)
![django version](https://img.shields.io/pypi/djversions/graphene-django-tools)
![wheel](https://img.shields.io/pypi/wheel/graphene-django-tools)
![maintenance](https://img.shields.io/maintenance/yes/2020)
[![Conventional Commits](https://img.shields.io/badge/Conventional%20Commits-1.0.0-yellow.svg)](https://conventionalcommits.org)

Tools for use [`graphene-django`](https://github.com/graphql-python/graphene-django)

Documentation is placed in [docs folder](./docs).

## Install

`pip install graphene-django-tools`

## Features

- django integration for [graphene-resolver](https://github.com/NateScarlet/graphene-resolver).
- optimize queryset with django `only`,`selected_related`,`prefetch_related` to only select fields that used in query.

### Query

- `ModelField`
- `ModelConnectionField`
- `ModelFilterConnectionField`

[example schema](./demo/api/schema.py)

Map the user model with filter in 10 lines.

![](./pic/20181012161945.png)
![](./pic/20181012162201.png)

### Mutation

- `ModelMutation`
- `ModelCreateMutation`
- `ModelUpdateMutation`

example: [`graphene_django_tools.auth` module](./graphene_django_tools/auth.py)

Map the user model with password validation in 40 lines.

![](./pic/20181011195459.png)
![](./pic/20181011200840.png)
![](./pic/20181012184432.png)

### Re-implemented `Mutation` class

Supports arguments on interface.

```python
class ClientMutationID(graphene.Interface):
    """Mutation with a client mutation id.  """

    class Arguments:
        client_mutation_id = graphene.String()

    client_mutation_id = graphene.String()
```

### Data loader integrate

Enable by add `'graphene_django_tools.dataloader.middleware.DataLoaderMiddleware'` to your django settings `GRAPHENE['MIDDLEWARE']`

When enabled, you will have `get_data_loader` method on your resolve context object.
It takes a django model type as argument, and returns corresponding `promise.DataLoader`.
Data loader is cached in request scope with `data_loader_cache` key.

## Development

run dev server: `make dev`

test: `make test`
