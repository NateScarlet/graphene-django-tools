
"""Mutatiom base for django model  """


import re
from collections import OrderedDict
from typing import Dict, Union

import django
import graphene
from django.db.models.fields.reverse_related import ForeignObjectRel
from graphene.types.unmountedtype import UnmountedType
from graphene_django.forms.converter import convert_form_field

from . import core
from ..texttools import snake_case
from ..types import ModelField
from .clientid import ClientIDMutation


class ModelMutaion(ClientIDMutation):
    """Mutate django model.  """
    # pylint: disable=abstract-method
    class Meta:
        abstract = True

    @classmethod
    def __init_subclass_with_meta__(cls, **options):
        if '_meta' not in options:
            options['_meta'] = cls._construct_meta(**options)

        super().__init_subclass_with_meta__(**options)

    @classmethod
    def _construct_meta(cls, **options) -> core.ModelMutationOptions:
        model = options['model']  # type: django.db.models.Model

        options.setdefault('_meta', core.ModelMutationOptions(cls))
        options.setdefault('node_fieldname', snake_case(model.__name__))
        options.setdefault('require', ())
        options.setdefault('exclude', ())

        ret = super()._construct_meta(**options)  # type: ModelMutationOptions
        ret.model = model
        ret.node_fieldname = options['node_fieldname']
        ret.require = options['require']
        ret.exclude = options['exclude']
        return ret

    @classmethod
    def _make_arguments_fields(cls, **options) -> OrderedDict:
        ret = super()._make_arguments_fields(**options)

        field_dict = OrderedDict(
            Meta=dict(description=f'Mapping data for model: {cls.__name__}'))
        field_dict.update(cls.collect_model_fields(**options))
        field_objecttype = type(
            re.sub("Mapping$|$", "Mapping", cls.__name__),
            (graphene.InputObjectType,),
            field_dict)
        field = field_objecttype(required=True)

        ret['mapping'] = field
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
    def _make_response_fields(cls, **options) -> OrderedDict:
        model = options['model']  # type: django.db.models.Model
        ret = super()._make_response_fields(**options)
        ret[options['node_fieldname']] = ModelField(model)
        return ret

    @classmethod
    def _make_context(cls, root, info: core.ResolveInfo, **kwargs):
        return core.ModelMutaionContext(
            root=root,
            info=info,
            options=cls._meta,
            arguments=kwargs,
            mapping=kwargs['mapping'])

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
    def mutate(cls, context: core.ModelMutaionContext)\
            -> graphene.ObjectType:

        return cls(**{context.options.node_fieldname: context.instance})

    @classmethod
    def postmutate(cls,
                   context: core.ModelMutaionContext,
                   response: graphene.ObjectType) -> graphene.ObjectType:
        ret = super().postmutate(context, response)
        context.instance.save()
        return ret


class ModelCreationMutaion(ModelMutaion):
    """Carete model.  """

    class Meta:
        abstract = True

    @classmethod
    def premutate(cls, context: core.ModelMutaionContext):
        super().premutate(context)
        instance = context.options.model(**context.mapping)
        context.instance = instance


class ModelUpdateMutaion(ModelMutaion):
    """Update model.  """

    class Meta:
        abstract = True

    @classmethod
    def _make_arguments_fields(cls, **options) -> OrderedDict:
        ret = super()._make_arguments_fields(**options)
        ret['id'] = graphene.ID(required=True).Argument()
        return ret

    @classmethod
    def premutate(cls, context: core.ModelMutaionContext):

        super().premutate(context)
        node = graphene.Node.get_node_from_global_id(
            context.info, global_id=context.arguments['id'])

        context.instance = node

    @classmethod
    def mutate(cls, context: core.ModelMutaionContext):
        for k, v in context.mapping.items():
            setattr(context.instance, k, v)
        return super().mutate(context)
