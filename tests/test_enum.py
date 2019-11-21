

import graphene

import graphene_django_tools as gdtools


def test_simple():

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
    result = schema.execute('''\
{
    foo
}
''')
    assert not result.errors
    assert result.data == {"foo": "a"}


def test_description():

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
