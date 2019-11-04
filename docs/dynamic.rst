Dynamic type
===============================

Use string as type to refer class that not defined yet.

when resolver called `as_field` or `as_type`, related type will be registered in 
``resolver.GRAPHENE_TYPE_REGISTRY``.

when same name registered multiple time, registry will keep latest type.

.. code:: python

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
  Pet.as_type('Pet')

  class Query(graphene.ObjectType):
      first_pet = FirstPet.as_field()
