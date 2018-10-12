
"""Anothor implement for `graphene.Mutation`  """

from collections import OrderedDict
from typing import Any, Dict, Type

import graphene
import graphene_django
import graphene_django.forms.mutation
from graphene.types.utils import yank_fields_from_attrs
from graphene.utils.get_unbound_function import get_unbound_function
from graphene.utils.props import props
from graphql.execution.base import ResolveInfo

from . import core


class Mutation(graphene.ObjectType):
    """Base mutation class.  """

    class Meta:
        abstract = True

    @classmethod
    def __init_subclass_with_meta__(cls, **options):
        # pylint: disable=W0221
        if '_meta' not in options:
            options['_meta'] = cls._construct_meta(**options)

        allowed_keys = ('_meta', 'name', 'description',
                        'interfaces', 'possible_types', 'default_resolver')
        options = {k: v for k, v in options.items() if k in allowed_keys}
        super().__init_subclass_with_meta__(**options)

    @classmethod
    def _construct_meta(cls, **options) -> graphene_django.forms.mutation.MutationOptions:
        ret = options.get(
            '_meta', graphene_django.forms.mutation.MutationOptions(cls))
        ret.output = cls._make_output_nodetype(**options)
        ret.resolver = cls._make_resolver(**options)
        ret.arguments = cls._make_arguments(**options)
        ret.fields = cls._make_fields(**options)
        return ret

    @classmethod
    def _make_output_nodetype(cls, **options) -> Type[graphene.ObjectType]:
        ret = options.get('output', getattr(cls, 'Output', cls))
        assert issubclass(ret, graphene.ObjectType), (cls, type(ret), options)
        return ret

    @classmethod
    def _make_fields(cls, **options) -> OrderedDict:
        if 'output' in options:
            return options['output'].fields

        ret = getattr(options.get('_meta'), 'fields', None) or OrderedDict()
        for base in reversed(cls.__mro__):
            _fields = yank_fields_from_attrs(base.__dict__,
                                             _as=graphene.Field)
            ret.update(_fields)
        return ret

    @classmethod
    def _make_arguments(cls, **options) -> OrderedDict:
        ret = options.get('arguments', OrderedDict())
        if hasattr(cls, 'Arguments'):
            ret.update(props(getattr(cls, 'Arguments')))
        return ret

    @classmethod
    def _make_resolver(cls, **options):
        # pylint: disable=unused-argument
        return get_unbound_function(cls._resolver)

    @classmethod
    def _resolver(cls, root, info: ResolveInfo, **kwargs: Dict[str, Any]):
        """Resolve the graphQL mutate.

        Only override this on abstract object.
        For schema, use `preform_mutate` instead.
        """

        context = core.MutationContext(root, info, cls._meta, {})
        try:
            cls.premutate(context, **kwargs)
            ret = cls.mutate(context, **kwargs)
            ret = cls.postmutate(context, ret, **kwargs)
        except:
            import traceback
            traceback.print_exc()
            raise
        return ret

    @classmethod
    def mutate(cls, context: core.MutationContext, **kwargs: Dict[str, Any]) \
            -> graphene.ObjectType:
        """Do the mutation.  """

        raise NotImplementedError(
            f'Method not implemented: {cls.__name__}.mutate')

    @classmethod
    def premutate(cls, context: core.MutationContext, **kwargs: Dict[str, Any]):
        """Actions before mutation perform.

        raise a error to abort the mutation.
        """

    @classmethod
    def postmutate(cls, context: core.MutationContext,
                   result: graphene.ObjectType,
                   **arguments: Dict[str, Any]) -> graphene.ObjectType:
        """Actions after mutation performed.

        Returns:
            graphene.ObjectType: Result value.
        """
        # pylint:disable=unused-argument
        assert isinstance(
            result, graphene.ObjectType), \
            f'Wrong result type: {type(result)}'
        return result

    @classmethod
    def Field(cls, **kwargs) -> graphene.Field:
        """Create graphene Feild for the mutation.  """
        # pylint: disable=invalid-name
        assert issubclass(cls._meta.output, graphene.ObjectType), type(
            cls._meta.output)
        return graphene.Field(
            type=cls._meta.output,
            args=cls._meta.arguments,
            resolver=cls._meta.resolver,
            name=kwargs.get('name'),
            required=kwargs.get('required', False),
            default_value=kwargs.get('default_value'),
            description=kwargs.get('description', cls.__doc__),
            deprecation_reason=kwargs.get('deprecation_reason'),)
