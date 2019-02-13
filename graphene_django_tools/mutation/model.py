
"""Mutation base for django model  """


import re
from collections import OrderedDict
from collections.abc import Callable
from typing import Dict, Iterable, Tuple

import django
import graphene
from django.db import models, transaction
from graphene.types.unmountedtype import UnmountedType
from graphene_django.registry import Registry, get_global_registry
from graphql import GraphQLError

from . import core
from ..converter import convert_db_field_to_argument
from ..types import ModelField, ModelListField
from .node import NodeMutation, NodeUpdateMutation


def get_all_fields(model):
    """Get all fields from model."""

    # pylint: disable=protected-access
    meta: django.db.models.options.Options = model._meta
    return meta.get_fields()


def construct_argument_fields(
        model: models.Model,
        registry: Registry,
        include: Iterable[str],
        require: Iterable[str])-> OrderedDict:
    """Construct fields for argument.

    Args:
        model (models.Model): Django db model.
        registry (Registry): Graphene django registry.
        include (Iterable[str]): Include field names.
        require (Iterable[str]): Required(Non-null) fields names.

    Returns:
        OrderedDict: Fields
    """

    fields = [i for i in get_all_fields(model) if i.name in include]

    ret = OrderedDict()
    for i in fields:
        converted = convert_db_field_to_argument(i, registry)
        if not converted:
            continue
        converted.kwargs['required'] = i.name in require
        ret[i.name] = converted
    return ret


class ModelMutation(NodeMutation):
    """Mutate django model.  """
    # pylint: disable=abstract-method
    class Meta:
        abstract = True

    @classmethod
    def __init_subclass_with_meta__(cls, **options):
        options.setdefault('_meta', core.ModelMutationOptions(cls))
        options.setdefault('require', ())
        options.setdefault('exclude', ())
        options.setdefault('require_mapping', True)
        options.setdefault('registry', get_global_registry())
        assert isinstance(options['registry'], Registry)
        if(not isinstance(options.get('fields'), (Callable, Iterable))):
            raise ValueError(f'Meta options for `{cls.__name__}` require'
                             ' `fields` to be either callable or iterable.')
        super().__init_subclass_with_meta__(**options)

    @classmethod
    def _construct_meta(cls, **options) -> core.ModelMutationOptions:
        ret = super()._construct_meta(**options)  # type: core.ModelMutationOptions
        ret.model = options['model']
        ret.registry = options['registry']
        return ret

    @classmethod
    def _make_arguments_fields(cls, **options) -> OrderedDict:
        options.setdefault('arguments', {})

        options['arguments'].update(
            cls._make_model_arguments_fields(**options))
        ret = super()._make_arguments_fields(**options)
        return ret

    @classmethod
    def _make_model_arguments_fields(cls, **options) -> dict:
        model = options['model']

        field_dict = OrderedDict(
            __doc__=f'Mapping data for mutation: {cls.__name__}',
            Meta=dict())
        field_dict.update(cls._get_model_input_fields(**options))
        field_objecttype = type(
            re.sub("Mapping$|$", "Mapping", cls.__name__),
            (graphene.InputObjectType,),
            field_dict)
        field = field_objecttype(required=options['require_mapping'],
                                 description=f'Mapping data for model: {model.__name__}')

        return {'mapping': field}

    @classmethod
    def _make_payload_fields(cls, **options) -> OrderedDict:
        model = options['model']  # type: django.db.models.Model
        ret = super()._make_payload_fields(**options)
        ret[options['node_fieldname']] = ModelField(model)
        return ret

    @classmethod
    def _make_context(cls, root, info: core.ResolveInfo, **kwargs):
        arguments = kwargs['input']
        return core.ModelMutationContext(
            root=root,
            info=info,
            node=None,
            options=cls._meta,
            arguments=arguments,
            mapping=None)

    @classmethod
    def _get_model_input_fields(cls, **options)-> Dict[str, UnmountedType]:

        model = options['model']
        fields = options['fields']
        require = options['require']
        exclude = options['exclude']
        if callable(fields):
            fields = fields(model)
            fields = list(i.name if hasattr(i, 'name') else i
                          for i in fields)
        fields = [i for i in fields if i not in exclude]
        ret = construct_argument_fields(model,
                                        options['registry'],
                                        fields,
                                        require,)
        ret = graphene.types.utils.yank_fields_from_attrs(ret)
        return ret

    @classmethod
    def _get_model_fields(cls, **options) -> list:
        model = options['model']  # type: django.db.models.Model
        fields = options['fields']
        return (i for i in get_all_fields(model) if i.name in fields)

    @classmethod
    def premutate(cls, context: core.ModelMutationContext):
        super().premutate(context)
        if hasattr(context, 'mapping'):
            context.mapping = context.arguments['mapping']

    @classmethod
    def mutate(cls, context: core.ModelMutationContext)\
            -> graphene.ObjectType:

        return cls(**{context.options.node_fieldname: context.instance})

    @classmethod
    def postmutate(cls,
                   context: core.ModelMutationContext,
                   payload: graphene.ObjectType) -> graphene.ObjectType:
        ret = super().postmutate(context, payload)
        try:
            context.instance.save()
        except AttributeError:
            pass
        return ret

    @classmethod
    def sorted_mapping(cls,
                       context: core.ModelMutationContext,
                       mapping: dict) -> Tuple[dict, dict]:
        """Get sorted mapping by type.

        Args:
            context (core.ModelMutationContext): Mutation context

        Raises:
            ValueError: Try use auto field in mapping.

        Returns:
            Tuple[dict, dict]: normal mapping, many to many mapping
        """

        fields = get_all_fields(context.options.model)
        normal_mapping = dict(mapping)
        m2m_mapping = {}
        for i in fields:
            if i.name not in mapping:
                continue
            if isinstance(i, django.db.models.AutoField):
                raise ValueError('Assign to auto field is not allowed')
            elif isinstance(i, django.db.models.ManyToManyField):
                m2m_mapping[i.name] = normal_mapping.pop(i.name)

        return normal_mapping, m2m_mapping


class ModelCreationMutation(ModelMutation):
    """Create model.  """

    class Meta:
        abstract = True

    @classmethod
    def mutate(cls, context: core.ModelMutationContext)\
            -> graphene.ObjectType:
        context.instance = cls.create(context, context.mapping)
        return super().mutate(context)

    @classmethod
    def create(cls,
               context: core.ModelMutationContext,
               mapping: dict) -> django.db.models.Model:
        """Create instance from mapping.  """

        normal_mapping, m2m_mapping = cls.sorted_mapping(context, mapping)
        instance = context.options.model(**normal_mapping)
        instance.save()
        for k, v in m2m_mapping.items():
            getattr(instance, k).set(v)
        return instance


class ModelUpdateMutation(NodeUpdateMutation, ModelMutation):
    """Update model.  """

    class Meta:
        abstract = True

    @classmethod
    def _construct_meta(cls, **options) -> core.ModelUpdateMutationOptions:
        options.setdefault('_meta', core.ModelUpdateMutationOptions(cls))
        ret = super()._construct_meta(**options) \
            # type: core.ModelUpdateMutationOptions
        return ret

    @classmethod
    def premutate(cls, context: core.ModelMutationContext):

        super().premutate(context)
        if not (isinstance(context.node, context.options.model)
                or (isinstance(context.node, list)
                    and all(isinstance(i, context.options.model) for i in context.node))):
            raise GraphQLError(
                f'Got a {type(context.node)} node, expected for {context.options.model}')
        context.instance = context.node

    @classmethod
    def mutate(cls, context: core.ModelMutationContext):
        normal_mapping, m2m_mapping = cls.sorted_mapping(
            context, context.mapping)
        for k, v in normal_mapping.items():
            setattr(context.instance, k, v)
        for k, v in m2m_mapping.items():
            getattr(context.instance, k).set(v)
        return super().mutate(context)


class ModelBulkMutation(ModelMutation):
    class Meta:
        abstract = True

    @classmethod
    def __init_subclass_with_meta__(cls, **options):
        options.setdefault('node_fieldname', 'node_set')
        super().__init_subclass_with_meta__(**options)

    @classmethod
    def _make_payload_fields(cls, **options) -> OrderedDict:
        model = options['model']  # type: django.db.models.Model
        ret = super()._make_payload_fields(**options)
        node_fieldname = options['node_fieldname']
        ret[node_fieldname] = ModelListField(model)
        return ret


class ModelBulkCreationMutation(ModelCreationMutation, ModelBulkMutation):
    """Create model in bulk.  """

    class Meta:
        abstract = True

    @classmethod
    def _make_context(cls, root, info: core.ResolveInfo, **kwargs):
        arguments = kwargs['input']
        return core.ModelBulkCreationMutationContext(
            root=root,
            info=info,
            options=cls._meta,
            arguments=arguments,
            data=None)

    @classmethod
    def premutate(cls, context: core.ModelBulkCreationMutationContext):
        super().premutate(context)
        context.data = context.arguments['data']

    @classmethod
    def _make_model_arguments_fields(cls, **options) -> dict:
        ret = super()._make_model_arguments_fields(**options)
        ret['data'] = graphene.List(ret.pop('mapping').__class__)
        return ret

    @classmethod
    def mutate(cls, context: core.ModelBulkCreationMutationContext)\
            -> graphene.ObjectType:
        ret = []
        for i in context.data:
            ret.append(cls.create(context, i))
        return cls(**{context.options.node_fieldname: ret})


class ModelBulkUpdateMutation(ModelUpdateMutation, ModelBulkMutation):
    """Update model in bulk.  """

    class Meta:
        abstract = True

    @classmethod
    def _make_node_arguments_fields(cls, **options) -> dict:
        id_fieldname = options['id_fieldname']
        ret = super()._make_node_arguments_fields(**options)
        ret[id_fieldname] = graphene.List(ret[id_fieldname].__class__).Field()
        return ret

    @classmethod
    def premutate(cls, context: core.ModelBulkUpdateMutationContext):
        super().premutate(context)
        assert isinstance(context.node, list) and all(isinstance(
            i, context.options.model) for i in context.node)
        context.query_set = context.options.model.objects.filter(
            pk__in=(i.pk for i in context.node))

    @classmethod
    @transaction.atomic
    def mutate(cls, context: core.ModelMutationContext):
        normal_mapping, m2m_mapping = cls.sorted_mapping(
            context, context.mapping)
        context.query_set.update(**normal_mapping)
        for i in context.query_set:
            for k, v in m2m_mapping.items():
                getattr(i, k).set(v)
            i.save()
        return cls(**{context.options.node_fieldname: context.query_set})
