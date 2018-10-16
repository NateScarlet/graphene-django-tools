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
        options.setdefault('node_fieldname', 'node')
        options.setdefault('interfaces', ())
        options['interfaces'] += (ClientMutationID,)
        super().__init_subclass_with_meta__(**options)

    @classmethod
    def _make_arguments_fields(cls, **options) -> dict:
        fields = super()._make_arguments_fields(**options)
        fields.update(
            __doc__=f'Input data for mutation: {cls.__name__}.',
            client_mutation_id=graphene.ID(
                description='Mutation id for relay, will be returned as-is.'))

        field_objecttype = type(
            re.sub("Input$|$", "Input", cls.__name__),
            (graphene.InputObjectType,),
            fields)
        field = field_objecttype(required=True,
                                 description='Input data this mutation.')
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


class NodeUpdateMutation(NodeMutation):
    """Mutate a node.  """
    # pylint: disable=abstract-method

    class Meta:
        abstract = True

    @classmethod
    def _construct_meta(cls, **options) -> core.NodeUpdateMutationOptions:
        options.setdefault('_meta', core.NodeUpdateMutationOptions(cls))
        options.setdefault('id_fieldname', 'id')

        ret = super()._construct_meta(**options) \
            # type: core.ModelUpdateMutationOptions
        ret.id_fieldname = options['id_fieldname']
        return ret

    @classmethod
    def _make_arguments_fields(cls, **options) -> dict:
        options.setdefault('arguments', {})

        id_type = graphene.ID(
            required=True,
            description='Node ID for this mutation.')
        options['arguments'][options['id_fieldname']] = id_type

        return super()._make_arguments_fields(**options)

    @classmethod
    def premutate(cls, context: core.ModelMutaionContext):

        id_ = context.arguments[cls._meta.id_fieldname]

        super().premutate(context)
        node = graphene.Node.get_node_from_global_id(
            context.info, global_id=id_)
        if not node:
            raise ValueError('No such node.', id_)
        context.node = node
