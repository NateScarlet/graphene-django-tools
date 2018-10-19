"""Anothor implement for `graphene.relay.mutation.ClientIDMutation`  """

import re
from typing import Type, Union

import graphene

from . import core
from ..interfaces import ClientMutationID
from .base import Mutation


def try_get_node(info: core.ResolveInfo, global_id: str, only_type: Type = False) \
        ->Union[graphene.Node, str]:
    """Fallback to global_id when `graphene.Node.get_node_from_global_id` 
        failed.

    Returns:
        Union[graphene.Node, str]: Node or input `global_id`
    """

    try:
        ret = graphene.Node.get_node_from_global_id(
            info=info, global_id=global_id, only_type=only_type)
    except AssertionError:
        ret = None
    if ret is None:
        ret = global_id
    return ret


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
        return core.NodeMutationContext(root=root,
                                        info=info,
                                        node=None,
                                        options=cls._meta,
                                        arguments=arguments)

    @classmethod
    def premutate(cls, context: core.ModelMutaionContext):
        super().premutate(context)
        for k, v in context.arguments.items():
            field = getattr(
                context.options.arguments['input'], '_meta').fields[k]
            context.arguments[k] = \
                cls._convert_id_field_to_node(context, field, v)

    @classmethod
    def _convert_id_field_to_node(cls,
                                  context: core.NodeMutationContext,
                                  field: graphene.types.mountedtype.MountedType,
                                  value):
        assert isinstance(
            field, graphene.types.mountedtype.MountedType), type(field)

        unmounted = field.type
        if isinstance(unmounted, graphene.NonNull):
            unmounted = unmounted.of_type

        # XXX: maybe replace this with single dispacth.
        if isinstance(unmounted, graphene.types.unmountedtype.UnmountedType):
            method = cls._id2node_unmmounted_instance
        elif issubclass(unmounted, graphene.InputObjectType):
            method = cls._id2node_inputobjecttype
        elif issubclass(unmounted, graphene.Scalar):
            method = cls._id2node_scalar
        else:
            raise NotImplementedError(unmounted)

        return method(context, unmounted, value)

    @classmethod
    def _id2node_unmmounted_instance(cls,
                                     context,
                                     unmounted: graphene.types.unmountedtype.UnmountedType,
                                     value):
        ret = value
        if isinstance(unmounted, graphene.List):
            assert isinstance(value, list), type(value)
            if issubclass(unmounted.of_type, graphene.ID):
                ret = [try_get_node(context.info, global_id=i) for i in value]
        else:
            raise NotImplementedError(unmounted)
        return ret

    @classmethod
    def _id2node_inputobjecttype(cls,
                                 context,
                                 unmounted: Type[graphene.Scalar],
                                 value):
        assert isinstance(value, dict), type(value)
        _input_fields = getattr(unmounted, '_meta').fields
        ret = {}
        for k, v in _input_fields.items():
            if k not in value:
                continue
            ret[k] = cls._convert_id_field_to_node(context, v, value[k])
        return ret

    @classmethod
    def _id2node_scalar(cls,
                        context,
                        unmounted: Type[graphene.InputObjectType],
                        value):
        ret = value
        if issubclass(unmounted, graphene.ID):
            ret = try_get_node(context.info, global_id=value)
        return ret

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
    def premutate(cls, context: core.NodeUpdateMutationOptions):
        super().premutate(context)
        node = context.arguments[context.options.id_fieldname]
        if not node:
            raise ValueError('No such node.')
        context.node = node