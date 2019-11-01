Connection
====================

Use ``ConnectionResolver`` to quick create relay compatible resolver.

.. code:: python

  import graphene
  import graphene_django_tools as gdtools
  from django.db import models

  class Item(gdtools.Resolver):
      schema = {'name': 'String!'}

  class ItemConnection(gdtools.ConnectionResolver):
      schema = {'node': Item}

  class Items(ItemConnection):
      def resolve(self, **kwargs):
          return self.resolve_connection([{'name': 'a'}, {'name': 'b'}], **kwargs)

  class Query(graphene.ObjectType):
      items = Items.as_field()
