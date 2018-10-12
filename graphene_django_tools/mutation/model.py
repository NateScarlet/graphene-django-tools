
"""Mutatiom base for django model  """


import re
from collections import OrderedDict
from typing import Any, Dict, List, Union

import django
import graphene
from django.db.models.fields.reverse_related import ForeignObjectRel
from graphene_django.forms.converter import convert_form_field

from . import core
from ..core import get_modelnode
from ..texttools import snake_case
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
        options.setdefault('nodename', snake_case(model.__name__))
        options.setdefault('require_arguments', ())
        options.setdefault('exclude_arguments', ())

        ret = super()._construct_meta(**options)  # type: ModelMutationOptions
        ret.model = model
        ret.nodename = options['nodename']
        ret.require_arguments = options['require_arguments']
        ret.exclude_arguments = options['exclude_arguments']
        return ret

    @classmethod
    def _make_arguments(cls, **options) -> OrderedDict:
        options.setdefault('arguments', OrderedDict())
        model = options['model']  # type: django.db.models.Model
        nodename = options['nodename']

        fields = model._meta.get_fields()  # pylint: disable=protected-access

        node_cls = type(
            re.sub("Input$|$", "Input", cls.__name__),
            (graphene.InputObjectType,),
            {i.name: cls._convert_db_field(i, **options)
             for i in cls.collect_arguments(fields, **options)})
        node = node_cls(required=True)  # type: graphene.InputObjectType

        options['arguments'].update({nodename: node})

        return super()._make_arguments(**options)

    @classmethod
    def _convert_db_field(cls, field: django.db.models.Field, **options) \
            -> Union[graphene.Field, None]:
        if isinstance(field, ForeignObjectRel):
            return None
        if field.name in options['exclude_arguments']:
            return None

        required = field.name in options['require_arguments']

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
    def _make_fields(cls, **options) -> OrderedDict:
        model = options['model']  # type: django.db.models.Model

        ret = super()._make_fields(**options)

        ret[options['nodename']] = graphene.Field(get_modelnode(model))
        return ret

    @classmethod
    def collect_arguments(cls,
                          fields: List[Union[django.db.models.Field, None]],
                          **options)\
            -> List[django.db.models.Field]:
        """Collect mutation argument fields.

        Field.required attribute can be changed here.
        """
        # pylint: disable=unused-argument

        ret = fields
        ret = [i for i in ret if i]
        return ret

    @classmethod
    def premutate(cls, context: core.MutationContext, **kwargs: Dict[str, Any]):
        super().premutate(context, **kwargs)
        context.data['nodedata'] = kwargs[context.meta.nodename]

    @classmethod
    def mutate(cls, context: core.MutationContext, **kwargs: Dict[str, Any]) \
            -> graphene.ObjectType:

        instance = context.data['instance']
        return cls(**{context.meta.nodename: instance})

    @classmethod
    def postmutate(cls, context: core.MutationContext,
                   result: graphene.ObjectType,
                   **kwargs: Dict[str, Any]) -> graphene.ObjectType:

        ret = super().postmutate(context, result, **kwargs)
        context.data['instance'].save()
        return ret


class ModelCreationMutaion(ModelMutaion):
    """Carete model.  """

    class Meta:
        abstract = True

    @classmethod
    def premutate(cls, context: core.MutationContext, **arguments: Dict[str, Any]):
        super().premutate(context, **arguments)
        instance = context.meta.model(**context.data['nodedata'])
        context.data['instance'] = instance


class ModelUpdateMutaion(ModelMutaion):
    """Update model.  """

    class Meta:
        abstract = True

    @classmethod
    def premutate(cls, context: core.MutationContext, **arguments: Dict[str, Any]):
        super().premutate(context, **arguments)
        instance = context.meta.model.objects.get(**context.data['nodedata'])
        context.data['instance'] = instance
