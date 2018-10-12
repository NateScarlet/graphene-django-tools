"""Mixin for predefined fieldss.  """

import graphene


class MessageMutation(graphene.Interface):
    """Mutation with a message.  """

    message = graphene.String(description='Human-readable execution status.')
