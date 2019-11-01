# pylint:disable=missing-docstring,invalid-name
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
