Node
=======================

use ``Resolver`` to define a relay node.

``validate`` method is required to determinate value type when using graphql interface or union.

example:

.. code:: python

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
