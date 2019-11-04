Resolver
======================

Allow create graphql schema with `apollo-like <https://www.apollographql.com/docs/tutorial/resolvers/#what-is-a-resolver>`_
resolver and and mongoose-like schema by using the ``Resolver`` class.

Python doc string will be used as field description.

Example
-------------------

Mutation that returns a scalar type:

.. code:: python

  import graphene
  import graphene_django_tools as gdtools

  class SomeMutation(gdtools.Resolver):
      schema = {
          "args": {
              "key": {
                "type": 'String',
                "required": True,
              },
              "value": 'String',
          },
          "type": 'Int',
          "description": "created from `Resolver`."
      }

      def resolve(self, **kwargs):
          print({"kwargs": kwargs})
          self.parent # parent field
          self.info # resolve info
          self.context # django request object
          return 42

  class Mutation(graphene.ObjectType):
      some_mutation = SomeMutation.as_field()

Mutation that returns a object type:

.. code:: python

  import graphene
  import graphene_django_tools as gdtools

  class SomeMutation(gdtools.Resolver):
      schema = {
        "ok": {
            "type": 'Int',
            "required": True,
        },
      }

      def resolve(self, **kwargs):
          return {"ok": 1}

  class Mutation(graphene.ObjectType):
      some_mutation = SomeMutation.as_field()

Nested resolver:

.. code:: python

  import graphene
  import graphene_django_tools as gdtools

  class FooResolver(gdtools.Resolver):
      schema = 'Int'

      def resolve(self, **kwargs):
          print({"parent": self.parent})
          return self.parent['bar']


  class BarResolver(gdtools.Resolver):
      schema = {
          "args": {
              "bar": 'Int'
          },
          "type": {
              "foo": FooResolver
          },
      }

      def resolve(self, **kwargs):
          return kwargs

  class Query(graphene.ObjectType):
      nested_resolver = BarResolver.as_field()

Use gdl type name for built in type:

.. code:: python

  import graphene_django_tools as gdtools

  class FooResolver(gdtools.Resolver):
      schema = 'Int!'

      def resolve(self, **kwargs):
          return 42

Use enum:

.. code:: python

  import graphene
  import graphene_django_tools as gdtools

  class State(graphene.Enum):
      A = 1


  class EnumResolver(gdtools.Resolver):
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

Use field from django model(mainly for enum):

.. code:: python

  import graphene
  import graphene_django_tools as gdtools
  from django.db import models

  class Task(models.Model):
      state = models.CharField('state',
                              max_length=2,
                              choices=(
                                  ('A', 'A state'),
                                  ('B', 'B state'),
                              ))

  class ModelFieldResolver(gdtools.Resolver):
      schema = {
          'args': {
              'value': Task._meta.get_field('state')
          },
          'type': Task._meta.get_field('state')
      }

      def resolve(self, **kwargs):
          return kwargs['value']

More complicated example:

.. code:: python

  import graphene
  import graphene_django_tools as gdtools

  class ComplicatedResolver(gdtools.Resolver):
      _input_schema = {
          "type": {"type": 'String'},
          "data": [
              {
                  "type":
                  {
                      "key": {
                          "type": 'String',
                          "required": True,
                          "description": "<description>",
                      },
                      "value": 'Int',
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

  class Mutation(graphene.ObjectType):
      complicated_resolver = ComplicatedResolver.as_field()
