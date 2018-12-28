"""Mixin for predefined fields.  """

import graphene


class Message(graphene.Interface):
    """Mutation with a message.  """

    message = graphene.String(description='Human-readable execution status.')


class ClientMutationID(graphene.Interface):
    """Mutation with a client mutation id.  """

    class Arguments:
        client_mutation_id = graphene.String()

    client_mutation_id = graphene.String()
