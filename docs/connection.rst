Connection
====================

Use ``get_connection`` to quick create relay compatible github-like connection resolver.

same name will returns same resolver, base on `CONNECTION_REGISTRY`.

.. code:: python

  import graphene
  import graphene_django_tools as gdtools
  from django.db import models

  class Item(gdtools.Resolver):
      schema = {'name': 'String!'}

  class Items(gdtools.Resolver):
      schema = gdtools.get_connection(Item)

      def resolve(self, **kwargs):
          return gdtools.resolve_connection([{'name': 'a'}, {'name': 'b'}], **kwargs)

  class Query(graphene.ObjectType):
      items = Items.as_field()
