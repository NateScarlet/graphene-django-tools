
# pylint:disable=missing-docstring,invalid-name
import graphene

import graphene_django_tools as gdtools


def test_simple():

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
    result = schema.execute('''\
{
    foo{
      __typename
      ... on Foo0 {
        a
      }
    }
}
''')
    assert not result.errors
    assert result.data == {"foo": {"__typename": "Foo0", "a": 'a'}}
