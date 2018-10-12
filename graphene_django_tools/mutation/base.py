
"""Anothor implement for `graphene.Mutation`  """

import re
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
        options.setdefault('name', cls.__name__)
        options['name'] = re.sub("Response$|$", "Response", options['name'])

        allowed_keys = ('_meta', 'name', 'description',
                        'interfaces', 'possible_types', 'default_resolver')
        options = {k: v for k, v in options.items() if k in allowed_keys}
        super().__init_subclass_with_meta__(**options)

    @classmethod
    def _construct_meta(cls, **options) -> graphene_django.forms.mutation.MutationOptions:
        ret = options.get(
            '_meta', graphene_django.forms.mutation.MutationOptions(cls))
        ret.output = cls._make_response_objecttype(**options)
        ret.resolver = cls._make_resolver(**options)
        ret.arguments = cls._make_arguments_fields(**options)
        ret.fields = cls._make_response_fields(**options)
        return ret

    @classmethod
    def _make_response_objecttype(cls, **options) -> Type[graphene.ObjectType]:
        ret = options.get('output', getattr(cls, 'Output', cls))
        assert issubclass(ret, graphene.ObjectType), (cls, type(ret), options)
        return ret

    @classmethod
    def _make_response_fields(cls, **options) -> OrderedDict:
        if 'output' in options:
            return options['output'].fields

        ret = getattr(options.get('_meta'), 'fields', None) or OrderedDict()
        for base in reversed(cls.__mro__):
            _fields = yank_fields_from_attrs(base.__dict__,
                                             _as=graphene.Field)
            ret.update(_fields)
        return ret

    @classmethod
    def _make_arguments_fields(cls, **options) -> OrderedDict:
        ret = options.get('arguments', OrderedDict())
        if hasattr(cls, 'Arguments'):
            ret.update(props(getattr(cls, 'Arguments')))
        return ret

    @classmethod
    def _make_resolver(cls, **options):
        # pylint: disable=unused-argument
        return get_unbound_function(cls._resolver)

    @classmethod
    def _make_context(cls, root, info: ResolveInfo, **kwargs):
        return core.MutationContext(root=root, info=info, options=cls._meta, arguments=kwargs)

    @classmethod
    def _resolver(cls, *args, **kwargs: Dict[str, Any]):
        """Resolve the graphQL mutate.

        Only override this on abstract object.
        For schema, use `preform_mutate` instead.
        """

        try:
            context = cls._make_context(*args, **kwargs)
            cls.premutate(context)
            response = cls.mutate(context)
            response = cls.postmutate(context, response)
            return response
        except:
            core.handle_resolve_error()
            raise

    @classmethod
    def mutate(cls, context: core.MutationContext) \
            -> graphene.ObjectType:
        """Do the mutation.  """

        raise NotImplementedError(
            f'Method not implemented: {cls.__name__}.mutate')

    @classmethod
    def premutate(cls, context: core.MutationContext):
        """Actions before mutation perform.

        raise a error to abort the mutation.
        """

    @classmethod
    def postmutate(cls, context: core.MutationContext,
                   response: graphene.ObjectType) -> graphene.ObjectType:
        """Actions after mutation performed.

        Returns:
            graphene.ObjectType: Result value.
        """
        # pylint:disable=unused-argument
        assert isinstance(
            response, graphene.ObjectType), \
            f'Wrong response type: {type(response)}'
        return response

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
