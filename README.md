# Graphene django tools

Tools for use [`graphene-django`](https://github.com/graphql-python/graphene-django)

Only support python3.7

## Install

`pip install graphene-django-tools`

## MainFeature

### Query

- `ModelField`
- `ModelConnectionField`
- `ModelFilterConnectionField`

[example schema](./test_site/api/schema.py)

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
