"""Graphene connection.  """

import graphene


class CountableConnection(graphene.relay.Connection):
    """Extended connection with total count.  """

    class Meta:
        abstract = True

    total = graphene.Int()

    @staticmethod
    def resolve_total(root, _info):
        return root.length
