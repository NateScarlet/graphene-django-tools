# pylint:disable=missing-docstring,invalid-name,unused-variable
import graphene

import graphene_django_tools as gdtools


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
  pageInfo: PageInfoV2
  edges: [ItemConnectionEdge]
}

type ItemConnectionEdge {
  node: Item
  cursor: String!
}

type PageInfoV2 {
  hasNextPage: Boolean!
  hasPreviousPage: Boolean!
  startCursor: String
  endCursor: String
  total: Int!
}

type Query {
  items(first: Int, last: Int, before: String, after: String): ItemConnection
}
'''
    result = schema.execute('''\
{
    items{
        edges {
            node{
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
''')
    assert not result.errors
    assert result.data == {
        "items": {
            "edges": [
                {"node": {"name": "a"}, "cursor": "YXJyYXljb25uZWN0aW9uOjA="},
                {"node": {"name": "b"}, "cursor": "YXJyYXljb25uZWN0aW9uOjE="}],
            "pageInfo": {
                "total": 2,
                "hasNextPage": False,
                "hasPreviousPage": False,
                "startCursor": "YXJyYXljb25uZWN0aW9uOjA=",
                "endCursor": "YXJyYXljb25uZWN0aW9uOjE="}},
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
        edges {
            node{
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
''')
    assert not result.errors
    assert result.data == {
        "items": {
            "edges": [
                {"node": {"name": "a"}, "cursor": "YXJyYXljb25uZWN0aW9uOjA="},
                {"node": {"name": "b"}, "cursor": "YXJyYXljb25uZWN0aW9uOjE="}],
            "pageInfo": {
                "total": 2,
                "hasNextPage": False,
                "hasPreviousPage": False,
                "startCursor": "YXJyYXljb25uZWN0aW9uOjA=",
                "endCursor": "YXJyYXljb25uZWN0aW9uOjE="}},
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
  pageInfo: PageInfoV2
  edges: [BarConnectionEdge]
}

type BarConnectionEdge {
  node: Bar
  cursor: String!
}

type Foo {
  value: Int
}

type FooConnection {
  pageInfo: PageInfoV2
  edges: [FooConnectionEdge]
}

type FooConnectionEdge {
  node: Foo
  cursor: String!
}

type PageInfoV2 {
  hasNextPage: Boolean!
  hasPreviousPage: Boolean!
  startCursor: String
  endCursor: String
  total: Int!
}

type Query {
  fooList(extraArg: String, first: Int, last: Int, before: String, after: String): FooConnection
  barList(first: Int, last: Int, before: String, after: String): BarConnection
}
'''
