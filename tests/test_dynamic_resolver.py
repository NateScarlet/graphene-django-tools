# pylint:disable=missing-docstring,invalid-name,unused-variable

import pytest
import graphene

import graphene_django_tools as gdtools

from . import models


def test_simple():
    class FirstPet(gdtools.Resolver):
        schema = 'Pet!'

        def resolve(self, **kwargs):
            return {
                'name': 'pet1',
                'age': 1
            }

    class Pet(gdtools.Resolver):
        schema = {
            'name': models.Pet._meta.get_field('name'),
            'age': models.Pet._meta.get_field('age'),
        }

    class Query(graphene.ObjectType):
        first_pet = FirstPet.as_field()

    schema = graphene.Schema(query=Query)
    assert str(schema) == '''\
schema {
  query: Query
}

type Pet {
  name: String
  age: Int
}

type Query {
  firstPet: Pet!
}
'''
    result = schema.execute('''\
{
    firstPet{
        name
        age
    }
}
''')
    assert not result.errors
    assert result.data == {
        "firstPet": {"name": 'pet1',
                     'age': 1}
    }


@pytest.mark.django_db
def test_node():
    models.Pet.objects.create(name='pet1', age=1)

    class FirstPet(gdtools.Resolver):
        schema = 'Pet!'

        def resolve(self, **kwargs):
            return models.Pet.objects.first()

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
        first_pet = FirstPet.as_field()

    schema = graphene.Schema(query=Query)
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
  firstPet: Pet!
}
'''
    result = schema.execute('''\
{
    firstPet{
        name
        age
    }
}
''')
    assert not result.errors
    assert result.data == {
        "firstPet": {"name": 'pet1',
                     'age': 1}
    }
