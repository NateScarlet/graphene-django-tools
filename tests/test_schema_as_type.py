# pylint:disable=missing-docstring,invalid-name
import functools

import graphene

import graphene_django_tools.resolver.schema as schema_


def test_simple():
    schema = schema_.FieldDefinition.parse('Int', default={'name': 'Foo'})
    type_ = schema.as_type()
    assert isinstance(type_, functools.partial)
    mounted = schema.mount(
        as_=graphene.Field)
    assert isinstance(mounted, graphene.Field)
    mounted = schema.mount(
        as_=graphene.Argument)
    assert isinstance(mounted, graphene.Argument)
