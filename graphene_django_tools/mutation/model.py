
"""Mutatiom base for django model  """


import re
from collections import OrderedDict
from typing import Dict, Tuple, Union

import django
import graphene
from django.db.models.fields.reverse_related import ForeignObjectRel
from graphene.types.unmountedtype import UnmountedType
from graphene_django.forms.converter import convert_form_field
from graphql import GraphQLError

from . import core
from ..texttools import snake_case
from ..types import ModelField
from .node import NodeMutation, NodeUpdateMutation


class ModelMutaion(NodeMutation):
    """Mutate django model.  """
    # pylint: disable=abstract-method
    class Meta:
        abstract = True

    @classmethod
    def _construct_meta(cls, **options) -> core.ModelMutationOptions:
        model = options['model']  # type: django.db.models.Model

        options.setdefault('_meta', core.ModelMutationOptions(cls))
        options.setdefault('node_fieldname', snake_case(model.__name__))
        options.setdefault('require', ())
        options.setdefault('exclude', ())

        ret = super()._construct_meta(**options)  # type: core.ModelMutationOptions
        ret.model = model
        ret.node_fieldname = options['node_fieldname']
        ret.require = options['require']
        ret.exclude = options['exclude']
        return ret

    @classmethod
    def _make_arguments_fields(cls, **options) -> OrderedDict:
        model = options['model']
        options.setdefault('arguments', {})
        field_dict = OrderedDict(
            __doc__=f'Mapping data for mutation: {cls.__name__}',
            Meta=dict())
        field_dict.update(cls.collect_model_fields(**options))
        field_objecttype = type(
            re.sub("Mapping$|$", "Mapping", cls.__name__),
            (graphene.InputObjectType,),
            field_dict)
        field = field_objecttype(required=True,
                                 description=f'Mapping data for model: {model.__name__}')

        options['arguments'].update(mapping=field)
        ret = super()._make_arguments_fields(**options)
        return ret

    @classmethod
    def _convert_db_field(cls, field: django.db.models.Field, **options)\
            -> Union[UnmountedType, None]:
        if isinstance(field, ForeignObjectRel):
            return None
        if field.name in options['exclude']:
            return None

        required = field.name in options['require']

        _field = field.formfield(required=required)
        if not _field:
            return None
        ret = convert_form_field(_field)  # pylint:disable=E1111

        # `convert_form_field` always return required field.
        # https://github.com/graphql-python/graphene-django/issues/532
        if isinstance(ret, graphene.Boolean):
            ret = graphene.Boolean(
                description=field.help_text,
                required=required)

        return ret

    @classmethod
    def _make_payload_fields(cls, **options) -> OrderedDict:
        model = options['model']  # type: django.db.models.Model
        ret = super()._make_payload_fields(**options)
        ret[options['node_fieldname']] = ModelField(model)
        return ret

    @classmethod
    def _make_context(cls, root, info: core.ResolveInfo, **kwargs):
        arguments = kwargs['input']
        return core.ModelMutaionContext(
            root=root,
            info=info,
            node=None,
            options=cls._meta,
            arguments=arguments,
            mapping=None)

    @classmethod
    def collect_model_fields(cls, **options)-> Dict[str, UnmountedType]:
        """Collect fields from model.  """

        model = options['model']  # type: django.db.models.Model
        fields = model._meta.get_fields()  # pylint: disable=protected-access
        ret = {i.name: cls._convert_db_field(i, **options)
               for i in fields}
        ret = graphene.types.utils.yank_fields_from_attrs(ret)
        return ret

    @classmethod
    def premutate(cls, context: core.ModelMutaionContext):
        super().premutate(context)
        context.mapping = context.arguments['mapping']

    @classmethod
    def mutate(cls, context: core.ModelMutaionContext)\
            -> graphene.ObjectType:

        return cls(**{context.options.node_fieldname: context.instance})

    @classmethod
    def postmutate(cls,
                   context: core.ModelMutaionContext,
                   payload: graphene.ObjectType) -> graphene.ObjectType:
        ret = super().postmutate(context, payload)
        context.instance.save()
        return ret

    @classmethod
    def sorted_mapping(cls,
                       context: core.ModelMutaionContext) -> Tuple[dict, dict]:
        """Get sorted mapping by type.

        Args:
            context (core.ModelMutaionContext): Mutation context

        Raises:
            ValueError: Try use auto field in mapping.

        Returns:
            Tuple[dict, dict]: normal mapping, many to many mapping
        """

        model_meta = getattr(context.options.model, '_meta')
        fields = model_meta.get_fields()
        normal_mapping = dict(context.mapping)
        m2m_mapping = {}
        for i in fields:
            if i.name not in context.mapping:
                continue
            if isinstance(i, django.db.models.AutoField):
                raise ValueError('Assign to auto field is not allowed')
            elif isinstance(i, django.db.models.ManyToManyField):
                m2m_mapping[i.name] = normal_mapping.pop(i.name)

        return normal_mapping, m2m_mapping


class ModelCreationMutaion(ModelMutaion):
    """Carete model.  """

    class Meta:
        abstract = True

    @classmethod
    def mutate(cls, context: core.ModelMutaionContext)\
            -> graphene.ObjectType:
        normal_mapping, m2m_mapping = cls.sorted_mapping(context)
        instance = context.options.model(**normal_mapping)
        instance.save()
        for k, v in m2m_mapping.items():
            getattr(instance, k).set(v)
        context.instance = instance
        return super().mutate(context)


class ModelUpdateMutaion(NodeUpdateMutation, ModelMutaion):
    """Update model.  """

    class Meta:
        abstract = True

    @classmethod
    def _construct_meta(cls, **options) -> core.ModelUpdateMutationOptions:
        model = options['model']  # type: django.db.models.Model

        options.setdefault('_meta', core.ModelUpdateMutationOptions(cls))
        options.setdefault('id_fieldname', snake_case(f'{model.__name__}_id'))
        ret = super()._construct_meta(**options) \
            # type: core.ModelUpdateMutationOptions
        return ret

    @classmethod
    def premutate(cls, context: core.ModelMutaionContext):

        super().premutate(context)
        if not isinstance(context.node, context.options.model):
            raise GraphQLError(
                f'Got a {type(context.node)} node, expected for {context.options.model}')
        context.instance = context.node

    @classmethod
    def mutate(cls, context: core.ModelMutaionContext):
        normal_mapping, m2m_mapping = cls.sorted_mapping(context)
        for k, v in normal_mapping.items():
            setattr(context.instance, k, v)
        for k, v in m2m_mapping.items():
            getattr(context.instance, k).set(v)
        return super().mutate(context)
