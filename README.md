# Graphene django tools

[![build status](https://github.com/NateScarlet/graphene-django-tools/workflows/Python%20package/badge.svg)](https://github.com/NateScarlet/graphene-django-tools/actions)
[![version](https://img.shields.io/pypi/v/graphene-django-tools)](https://pypi.org/project/graphene-django-tools/)
![python version](https://img.shields.io/pypi/pyversions/graphene-django-tools)
![django version](https://img.shields.io/pypi/djversions/graphene-django-tools)
![wheel](https://img.shields.io/pypi/wheel/graphene-django-tools)
![maintenance](https://img.shields.io/maintenance/yes/2019)
[![Conventional Commits](https://img.shields.io/badge/Conventional%20Commits-1.0.0-yellow.svg)](https://conventionalcommits.org)

Tools for use [`graphene-django`](https://github.com/graphql-python/graphene-django)

## Install

`pip install graphene-django-tools`

## Features

- easy resolver creation.
- github-like connection with totalCount.
- optimize queryset with django `only`,`selected_related`,`prefetch_related` to only select fields that used in query.

### Resolver

Using mongoose-like schema to write apollo-like resolver.

simple example:

```python
import graphene
import graphene_django_tools as gdtools

class Foo(gdtools.Resolver):
    schema = {
        "args": {
            "key":  'String!',
            "value": 'String!',
        },
        "type": 'String!',
    }

    def resolve(self, **kwargs):
        self.parent # parent field
        self.info # resolve info
        self.context # django request object
        return kwargs['value']

class Query(graphene.ObjectType):
    foo = Foo.as_field()
```

```graphql
{
  foo(key: "k", value: "v")
}
```

```json
{ "foo": "v" }
```

relay node:

```python
class Pet(gdtools.Resolver):
    schema = {
        'type': {
            'name': models.Pet._meta.get_field('name'),
            'age': models.Pet._meta.get_field('age'),
        },
        'interfaces': (graphene.Node,)
    }

    def get_node(self, id_):
        return models.Pet.objects.get(pk=id_)

    def validate(self, value):
        return isinstance(value, models.Pet)

class Query(graphene.ObjectType):
    node = graphene.Node.Field()

schema = graphene.Schema(query=Query, types=[Pet.as_type()])
```

```graphql
{
  node(id: "UGV0OjE=") {
    id
    __typename
    ... on Pet {
      name
      age
    }
  }
}
```

```json
{ "node": { "id": "UGV0OjE=", "__typename": "Pet", "name": "pet1", "age": 1 } }
```

relay connection:

```python
class Item(gdtools.Resolver):
    schema = {'name': 'String!'}

class Items(gdtools.Resolver):
    schema = gdtools.get_connection(Item)

    def resolve(self, **kwargs):
        return gdtools.resolve_connection([{'name': 'a'}, {'name': 'b'}], **kwargs)
```

```graphql
{
  items {
    edges {
      node {
        name
      }
      cursor
    }
    pageInfo {
      total
      hasNextPage
      hasPreviousPage
      startCursor
      endCursor
    }
  }
}
```

```json
{
  "items": {
    "edges": [
      { "node": { "name": "a" }, "cursor": "YXJyYXljb25uZWN0aW9uOjA=" },
      { "node": { "name": "b" }, "cursor": "YXJyYXljb25uZWN0aW9uOjE=" }
    ],
    "pageInfo": {
      "total": 2,
      "hasNextPage": false,
      "hasPreviousPage": false,
      "startCursor": "YXJyYXljb25uZWN0aW9uOjA=",
      "endCursor": "YXJyYXljb25uZWN0aW9uOjE="
    }
  }
}
```

enum:

```python

    class Foo(gdtools.Resolver):
        schema = ('a', 'b')

        def resolve(self, **kwargs):
            return 'a'

    class Query(graphene.ObjectType):
        foo = Foo.as_field()

    schema = graphene.Schema(query=Query)
    assert str(schema) == '''\
schema {
  query: Query
}

enum Foo {
  a
  b
}

type Query {
  foo: Foo
}
'''
```

enum with description:

```python

    class Foo(gdtools.Resolver):
        schema = {
            'type': [('a', 'this is a'), ('b', 'this is b'), 'c'],
            'description': 'A enum',
        }

        def resolve(self, **kwargs):
            return 'a'

    class Query(graphene.ObjectType):
        foo = Foo.as_field()

    schema = graphene.Schema(query=Query)
    enum_type = schema.get_type('Foo')
    assert enum_type.description == 'A enum'
    assert enum_type.get_value('a').value == 'a'
    assert enum_type.get_value('a').description == 'this is a'
    assert enum_type.get_value('b').value == 'b'
    assert enum_type.get_value('b').description == 'this is b'
    assert enum_type.get_value('c').value == 'c'
    assert enum_type.get_value('c').description is None
```

union:

```python
    class Foo(gdtools.Resolver):
        schema = ({'a': 'String'}, {'b': 'Int'})

        def resolve(self, **kwargs):
            return {'__typename': 'Foo0', 'a': 'a'}

    class Query(graphene.ObjectType):
        foo = Foo.as_field()

    schema = graphene.Schema(query=Query)
    assert str(schema) == '''\
schema {
  query: Query
}

union Foo = Foo0 | Foo1

type Foo0 {
  a: String
}

type Foo1 {
  b: Int
}

type Query {
  foo: Foo
}
'''
```

```graphql
{
  foo {
    __typename
    ... on Foo0 {
      a
    }
  }
}
```

```json
{ "foo": { "__typename": "Foo0", "a": "a" } }
```

complicated example:

```python
class Foo(gdtools.Resolver):
    _input_schema = {
        "type": {"type": 'String'},
        "data": [
            {
                "type":
                {
                    "key": {
                        "type": 'String',
                        "required": True,
                        "description": "<description>",
                    },
                    "value": 'Int',
                    "extra": {
                        "type": ['String!'],
                        "deprecation_reason": "<deprecated>"
                    },
                },
                "required": True
            },
        ],
    }
    schema = {
        "args": {
            "input": _input_schema
        },
        "type": _input_schema,
        "description": "description",
        "deprecation_reason": None
    }

    def resolve(self, **kwargs):
        return kwargs['input']
```

```graphql
{
  foo(
    input: { type: "type", data: [{ key: "key", value: 42, extra: ["extra"] }] }
  ) {
    type
    data {
      key
      value
      extra
    }
  }
}
```

```json
{
  "foo": {
    "type": "type",
    "data": [{ "key": "key", "value": 42, "extra": ["extra"] }]
  }
}
```

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
