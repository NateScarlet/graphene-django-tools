"""Graphene types for django model.  """

import graphene_django


class ModelNodeOptions(graphene_django.types.DjangoObjectTypeOptions):
    """Extended DjangoObjectTypeOptions for `ModelNode`.  """

    filterset_class = None
