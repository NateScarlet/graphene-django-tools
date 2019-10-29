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
                "type": str,
                "required: True,
              },
              "value": str,
          },
          "type": int,
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
            "type": int,
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
      schema = int

      def resolve(self, **kwargs):
          print({"parent": self.parent})
          return self.parent['bar']


  class BarResolver(gdtools.Resolver):
      schema = {
          "args": {
              "bar": int
          },
          "type": {
              "foo": FooResolver
          },
      }

      def resolve(self, **kwargs):
          return kwargs

  class Query(graphene.ObjectType):
      nested_resolver = BarResolver.as_field()


Full example:

.. code:: python

  import graphene
  import graphene_django_tools as gdtools

  class ComplicatedResolver(gdtools.Resolver):
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
                          "type": [str],
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
