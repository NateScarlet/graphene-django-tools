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
    def __init_subclass_with_meta__(cls, **options):
        options.setdefault('name', cls.__name__)
        options['name'] = re.sub("Payload$|$", "Payload", options['name'])
        super().__init_subclass_with_meta__(**options)

    @classmethod
    def _make_arguments(cls, **options) -> OrderedDict:
        options.setdefault('name', cls.__name__)
        options.setdefault('arguments', OrderedDict())
        options.setdefault('input_nodename', 'arguments')
        options['arguments'].update(
            client_mutation_id=graphene.Field.mounted(graphene.String()))

        arguments = super()._make_arguments(**options)

        node_cls = type(
            re.sub("Arguments$|$", "Arguments", options['name']),
            (graphene.InputObjectType,),
            arguments)
        node = node_cls(required=True)  # type: graphene.InputObjectType

        ret = OrderedDict({options['input_nodename']: node})
        return ret

    @classmethod
    def _make_fields(cls, **options) -> OrderedDict:
        ret = super()._make_fields(**options)
        ret['client_mutation_id'] = graphene.Field.mounted(graphene.String())
        return ret

    @classmethod
    def postmutate(cls, context: core.MutationContext,
                   result: graphene.ObjectType,
                   **arguments: Dict[str, Any]) -> graphene.ObjectType:

        result = super().postmutate(result, **arguments)
        result.client_mutation_id = arguments.get("client_mutation_id")
        return result
