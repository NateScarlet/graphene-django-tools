
# pylint:disable=missing-docstring,invalid-name

import functools
import inspect

import graphene

import graphene_django_tools as gdtools


def test_simple():
    class Foo(gdtools.Resolver):
        schema = {
            'args': {'a': 'Int'},
            'type': 'Int'
        }

    type_ = Foo.as_type()
    assert isinstance(type_, functools.partial)
    field = Foo.as_field()
    assert len(field.args) == 1
    assert all([isinstance(i, graphene.Argument)
                for i in field.args.values()]), field.args
    assert all([i._type
                for i in field.args.values()])
    assert all([i.type
                for i in field.args.values()])
    assert isinstance(field, graphene.Field)
    assert inspect.isfunction(field.resolver)
