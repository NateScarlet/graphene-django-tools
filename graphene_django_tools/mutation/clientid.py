"""Anothor implement for `graphene.relay.mutation.ClientIDMutation`  """

import re
from collections import OrderedDict
from typing import Any, Dict

import graphene

from . import core
from .base import Mutation


class ClientIDMutation(Mutation):
    """Mutation with auto client_mutation_id field.  """
    # pylint: disable=abstract-method

    class Meta:
        abstract = True

    @classmethod
    def _make_arguments_fields(cls, **options) -> OrderedDict:
        ret = super()._make_arguments_fields(**options)
        ret['client_mutation_id'] = graphene.String().Argument()
        return ret

    @classmethod
    def _make_response_fields(cls, **options) -> OrderedDict:
        ret = super()._make_response_fields(**options)
        ret['client_mutation_id'] = graphene.String().Field()
        return ret

    @classmethod
    def postmutate(cls,
                   context: core.MutationContext,
                   response: graphene.ObjectType) -> graphene.ObjectType:
        ret = super().postmutate(context, response)
        ret.client_mutation_id = context.arguments.get("client_mutation_id")
        return ret
