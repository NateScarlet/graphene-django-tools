# pylint:disable=missing-docstring,invalid-name
import pytest
import graphene

import graphene_django_tools as gdtools

from . import models


def test_simple():
    class Foo(gdtools.Resolver):
        schema = {
            "args": {
                "key":  'String!',
                "value": 'String!',
            },
            "type": 'String!',
        }

        def resolve(self, **kwargs):
            return kwargs['value']

    class Query(graphene.ObjectType):
        foo = Foo.as_field()

    schema = graphene.Schema(query=Query)
    result = schema.execute('''\
{
    foo(key: "k", value: "v")
}
''')
    assert not result.errors
    assert result.data == {"foo":  "v"}


def test_object():
    class Foo(gdtools.Resolver):
        schema = {
            "ok": {
                "type": int,
                "required": True,
            },
        }

        def resolve(self, **kwargs):
            return {"ok": 1}

    class Query(graphene.ObjectType):
        foo = Foo.as_field()

    schema = graphene.Schema(query=Query)
    result = schema.execute('''\
{
    foo{
        ok
    }
}
''')
    assert not result.errors
    assert result.data == {"foo": {"ok": 1}}


def test_nested():
    class Foo(gdtools.Resolver):
        schema = int

        def resolve(self, **kwargs):
            print({"parent": self.parent})
            return self.parent['bar']

    class Bar(gdtools.Resolver):
        schema = {
            "args": {
                "bar": int
            },
            "type": {
                "foo": Foo
            },
        }

        def resolve(self, **kwargs):
            return kwargs

    class Query(graphene.ObjectType):
        bar = Bar.as_field()

    schema = graphene.Schema(query=Query)
    result = schema.execute('''\
{
    bar(bar: 42){
        foo
    }
}
''')
    assert not result.errors
    assert result.data == {"bar": {"foo": 42}}


def test_enum():
    class State(graphene.Enum):
        A = 1

    class Foo(gdtools.Resolver):
        schema = {
            'args': {
                'value': {
                    'type': State,
                    'required': True
                },
            },
            'type': State
        }

        def resolve(self, **kwargs):
            return kwargs['value']

    class Query(graphene.ObjectType):
        foo = Foo.as_field()

    schema = graphene.Schema(query=Query)
    result = schema.execute('''\
{
    foo(value: A)
}
''')
    assert not result.errors
    assert result.data == {"foo": "A"}


def test_model():
    class Foo(gdtools.Resolver):
        schema = {
            'args': {
                'value': models.Reporter._meta.get_field('a_choice')
            },
            'type': models.Reporter._meta.get_field('a_choice')
        }

        def resolve(self, **kwargs):
            return kwargs['value']

    class Query(graphene.ObjectType):
        foo = Foo.as_field()

    schema = graphene.Schema(query=Query)
    result = schema.execute('''\
{
    foo(value: A_1)
}
''')
    assert not result.errors
    assert result.data == {"foo": "A_1"}


def test_complicated():
    class Foo(gdtools.Resolver):
        _input_schema = {
            "type": {"type": str},
            "data": [
                {
                    "type":
                    {
                        "key": {
                            "type": str,
                            "required": True,
                            "description": "<description>",
                        },
                        "value": int,
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

    class Query(graphene.ObjectType):
        foo = Foo.as_field()

    schema = graphene.Schema(query=Query)
    result = schema.execute('''\
{
    foo(input: {type: "type", data: [{key: "key", value: 42, extra: ["extra"]}]}){
        type
        data{
            key
            value
            extra
        }
    }
}
''')
    assert not result.errors
    assert result.data == {
        "foo": {"type": "type",
                "data": [{"key": "key", "value": 42, "extra": ["extra"]}]}}


@pytest.mark.django_db
def test_interface():
    models.Pet.objects.create(name='pet1', age=1)

    class Foo(gdtools.Resolver):
        schema = {
            'type': {
                'name': models.Pet._meta.get_field('name'),
                'age': models.Pet._meta.get_field('age'),
            },
            'interfaces': (graphene.Node,)
        }

        def resolve(self, **kwargs):
            return models.Pet.objects.first()

    class Query(graphene.ObjectType):
        foo = Foo.as_field()

    schema = graphene.Schema(query=Query)
    assert str(schema) == '''\
schema {
  query: Query
}

type Foo implements Node {
  id: ID!
  name: String
  age: Int
}

interface Node {
  id: ID!
}

type Query {
  foo: Foo
}
'''
    result = schema.execute('''\
{
    foo{
        id
        name
        age
    }
}
''')
    assert not result.errors
    assert result.data == {
        "foo": {"id": "Rm9vOjE=",
                "name": 'pet1',
                'age': 1}
    }


@pytest.mark.django_db
def test_node():
    models.Pet.objects.create(name='pet1', age=1)

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
    assert str(schema) == '''\
schema {
  query: Query
}

interface Node {
  id: ID!
}

type Pet implements Node {
  id: ID!
  name: String
  age: Int
}

type Query {
  node(id: ID!): Node
}
'''
    result = schema.execute('''\
{
    node(id: "UGV0OjE="){
        id
        __typename
        ... on Pet {
            name
            age
        }
    }
}
''')
    assert not result.errors
    assert result.data == {
        "node": {"id": "UGV0OjE=",
                 "__typename": "Pet",
                 "name": 'pet1',
                 'age': 1}
    }
