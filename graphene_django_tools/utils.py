"""Utility.  """

import graphene


class EmptyQuery(graphene.ObjectType):
    """Empty Query.  """

    placeholder = graphene.String()
