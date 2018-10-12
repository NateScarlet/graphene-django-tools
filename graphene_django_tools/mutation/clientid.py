"""Anothor implement for `graphene.relay.mutation.ClientIDMutation`  """

import graphene

from . import core
from ..interfaces import ClientMutationID
from .base import Mutation


class ClientIDMutation(Mutation):
    """Mutation with auto client_mutation_id field.  """
    # pylint: disable=abstract-method

    class Meta:
        abstract = True

    @classmethod
    def __init_subclass_with_meta__(cls, **options):
        options.setdefault('interfaces', ())
        options['interfaces'] += (ClientMutationID,)

        super().__init_subclass_with_meta__(**options)

    @classmethod
    def postmutate(cls,
                   context: core.MutationContext,
                   response: graphene.ObjectType) -> graphene.ObjectType:
        ret = super().postmutate(context, response)
        ret.client_mutation_id = context.arguments.get("client_mutation_id")
        return ret
