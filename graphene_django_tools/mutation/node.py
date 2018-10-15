"""Anothor implement for `graphene.relay.mutation.ClientIDMutation`  """

import re

import graphene

from . import core
from ..interfaces import ClientMutationID
from .base import Mutation


class NodeMutation(Mutation):
    """Mutation that supports relay.  """
    # pylint: disable=abstract-method

    class Meta:
        abstract = True

    @classmethod
    def __init_subclass_with_meta__(cls, **options):
        options.setdefault('interfaces', ())
        options['interfaces'] += (ClientMutationID,)

        super().__init_subclass_with_meta__(**options)

    @classmethod
    def _make_arguments_fields(cls, **options) -> dict:
        fields = super()._make_arguments_fields(**options)
        fields.update(client_mutation_id=graphene.ID(
            description='Mutation id for relay, will be returned as-is.'))

        field_objecttype = type(
            re.sub("Input$|$", "Input", cls.__name__),
            (graphene.InputObjectType,),
            fields)

        field = field_objecttype(required=True,
                                 description=f'Input data for mutation: {cls.__name__}')
        return dict(input=field)

    @classmethod
    def _make_context(cls, root, info: core.ResolveInfo, **kwargs):
        arguments = kwargs['input']
        return core.MutationContext(root=root,
                                    info=info,
                                    options=cls._meta,
                                    arguments=arguments)

    @classmethod
    def postmutate(cls,
                   context: core.MutationContext,
                   payload: graphene.ObjectType) -> graphene.ObjectType:
        ret = super().postmutate(context, payload)
        ret.client_mutation_id = context.arguments.get("client_mutation_id")
        return ret
