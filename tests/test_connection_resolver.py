# pylint:disable=missing-docstring,invalid-name,unused-variable
import django.db.models as djm
import graphene
import pytest

import graphene_django_tools as gdtools

from . import models


def test_simple():
    class Item(gdtools.Resolver):
        schema = {'name': 'String!'}

    class Items(gdtools.Resolver):
        schema = gdtools.get_connection(Item)

        def resolve(self, **kwargs):
            return gdtools.resolve_connection([{'name': 'a'}, {'name': 'b'}], **kwargs)

    class Query(graphene.ObjectType):
        items = Items.as_field()

    assert isinstance(Query.items, graphene.Field)
    assert isinstance(Query.items.type, type)
    assert issubclass(Query.items.type, graphene.ObjectType)

    schema = graphene.Schema(query=Query)
    assert str(schema) == '''\
schema {
  query: Query
}

type Item {
  name: String!
}

type ItemConnection {
  edges: [ItemEdge]
  nodes: [Item]
  pageInfo: PageInfo!
  totalCount: Int!
}

type ItemEdge {
  node: Item
  cursor: String!
}

type PageInfo {
  hasNextPage: Boolean!
  hasPreviousPage: Boolean!
  startCursor: String
  endCursor: String
}

type Query {
  items(after: String, before: String, first: Int, last: Int): ItemConnection
}
'''
    result = schema.execute('''\
{
    items{
        nodes{
            name
        }
        edges {
            node{
                name
            }
            cursor
        }
        pageInfo {
            hasNextPage
            hasPreviousPage
            startCursor
            endCursor
        }
        totalCount
    }
}
''')
    assert not result.errors
    assert result.data == {
        "items": {
            "nodes": [{"name": "a"}, {"name": "b"}],
            "edges": [
                {"node": {"name": "a"}, "cursor": "YXJyYXljb25uZWN0aW9uOjA="},
                {"node": {"name": "b"}, "cursor": "YXJyYXljb25uZWN0aW9uOjE="}],
            "pageInfo": {
                "hasNextPage": False,
                "hasPreviousPage": False,
                "startCursor": "YXJyYXljb25uZWN0aW9uOjA=",
                "endCursor": "YXJyYXljb25uZWN0aW9uOjE="},
            "totalCount": 2,
        },
    }


def test_dynamic():
    class Item(gdtools.Resolver):
        schema = {'name': 'String!'}

    class Items(gdtools.Resolver):
        schema = gdtools.get_connection('Item')

        def resolve(self, **kwargs):
            return gdtools.resolve_connection([{'name': 'a'}, {'name': 'b'}], **kwargs)

    class Query(graphene.ObjectType):
        items = Items.as_field()

    schema = graphene.Schema(query=Query)
    result = schema.execute('''\
{
    items{
        nodes {
            name
        }
        edges {
            node{
                name
            }
            cursor
        }
        pageInfo {
            hasNextPage
            hasPreviousPage
            startCursor
            endCursor
        }
        totalCount
    }
}
''')
    assert not result.errors
    assert result.data == {
        "items": {
            "nodes": [{"name": "a"}, {"name": "b"}],
            "edges": [
                {"node": {"name": "a"}, "cursor": "YXJyYXljb25uZWN0aW9uOjA="},
                {"node": {"name": "b"}, "cursor": "YXJyYXljb25uZWN0aW9uOjE="}],
            "pageInfo": {
                "hasNextPage": False,
                "hasPreviousPage": False,
                "startCursor": "YXJyYXljb25uZWN0aW9uOjA=",
                "endCursor": "YXJyYXljb25uZWN0aW9uOjE="},
            "totalCount": 2,
        },
    }


def test_name_conflict():
    class Foo(gdtools.Resolver):
        schema = {
            'value': 'Int'
        }

        def resolve(self, **kwargs):
            print({"parent": self.parent})
            return self.parent['bar']

    class Bar(gdtools.Resolver):
        schema = {
            'value': 'String'
        }

        def resolve(self, **kwargs):
            return kwargs

    class FooList(gdtools.Resolver):
        schema = {
            'args': {
                'extraArg': 'String'
            },
            'type': gdtools.get_connection('Foo')
        }

    class BarList(gdtools.Resolver):
        schema = gdtools.get_connection('Bar')

    class Query(graphene.ObjectType):
        foo_list = FooList.as_field()
        bar_list = BarList.as_field()

    schema = graphene.Schema(query=Query)
    assert str(schema) == '''\
schema {
  query: Query
}

type Bar {
  value: String
}

type BarConnection {
  edges: [BarEdge]
  nodes: [Bar]
  pageInfo: PageInfo!
  totalCount: Int!
}

type BarEdge {
  node: Bar
  cursor: String!
}

type Foo {
  value: Int
}

type FooConnection {
  edges: [FooEdge]
  nodes: [Foo]
  pageInfo: PageInfo!
  totalCount: Int!
}

type FooEdge {
  node: Foo
  cursor: String!
}

type PageInfo {
  hasNextPage: Boolean!
  hasPreviousPage: Boolean!
  startCursor: String
  endCursor: String
}

type Query {
  fooList(extraArg: String, after: String, before: String, first: Int, last: Int): FooConnection
  barList(after: String, before: String, first: Int, last: Int): BarConnection
}
'''


def test_lazy_resolve():
    class Item(gdtools.Resolver):
        schema = {'name': 'String!'}

    class Items(gdtools.Resolver):
        schema = gdtools.get_connection(Item)

        def resolve(self, **kwargs):
            class DummyIterable:
                def __len__(self):
                    return 10

            return gdtools.resolve_connection(DummyIterable(), **kwargs)

    class Query(graphene.ObjectType):
        items = Items.as_field()

    assert isinstance(Query.items, graphene.Field)
    assert isinstance(Query.items.type, type)
    assert issubclass(Query.items.type, graphene.ObjectType)

    schema = graphene.Schema(query=Query)
    result = schema.execute('''\
{
    items{
        totalCount
    }
}
''')
    assert not result.errors
    assert result.data == {
        "items": {
            "totalCount": 10,
        },
    }
    result = schema.execute('''\
{
    items{
        nodes{
            name
        }
    }
}
''')
    assert (str(result.errors) ==
            str([TypeError("'DummyIterable' object is not subscriptable")]))


@pytest.mark.django_db
def test_keep_queryset():

    result = gdtools.resolve_connection(models.Pet.objects.all(), first=1,)
    qs = result['nodes']
    assert isinstance(qs, djm.QuerySet)
    assert qs.model is models.Pet
