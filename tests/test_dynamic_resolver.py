
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

    Pet.as_type('Pet')
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
