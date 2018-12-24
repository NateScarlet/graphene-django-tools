"""Convert django field to graphene field for arguments.  """

from functools import singledispatch
from typing import Optional

import django
import graphene
from django import forms
from django.db import models
from graphene.types.json import JSONString
from graphene.types.unmountedtype import UnmountedType
from graphene_django.compat import (ArrayField, HStoreField, JSONField,
                                    RangeField)
from graphene_django.forms.converter import convert_form_field
from graphene_django.registry import Registry

from .enum import construct_enum_from_db_field


def convert_db_field_to_argument(
        field: django.db.models.Field, registry: Optional[Registry] = None) -> UnmountedType:
    """Convert a django db field to graphene field for argument.

    Args:
        field (django.db.models.Field): Field
        registry (Optional[Registry], optional): Defaults to None. Field registry.

    Returns:
        graphene.types.unmounted.UnmmountedType: Graphene field.
    """

    if getattr(field, "choices", None):
        ret = construct_enum_from_db_field(field, registry)
    else:
        ret = _convert_db_field_to_argument(field)
    return ret


@singledispatch
def _convert_db_field_to_argument(field):
    form_field = field.formfield()
    if not form_field:
        return None
    return convert_form_field(form_field)


@_convert_db_field_to_argument.register(models.BooleanField)
def _(field: models.BooleanField):
    return graphene.Boolean(description=field.help_text, required=not field.blank)


@_convert_db_field_to_argument.register(models.ForeignKey)
@_convert_db_field_to_argument.register(models.OneToOneField)
@_convert_db_field_to_argument.register(models.OneToOneRel)
def _(field):
    return graphene.ID(description=getattr(field, 'help_text', ''),
                       required=not getattr(field, 'blank', True))


@_convert_db_field_to_argument.register(models.ManyToManyField)
@_convert_db_field_to_argument.register(models.ManyToManyRel)
@_convert_db_field_to_argument.register(models.ManyToOneRel)
def _(field):
    return graphene.List(graphene.NonNull(graphene.ID), description=getattr(field, 'help_text', ''))


@_convert_db_field_to_argument.register(ArrayField)
@_convert_db_field_to_argument.register(RangeField)
def _(field):
    base_type = _convert_db_field_to_argument(field.base_field)
    if not isinstance(base_type, graphene.NonNull):
        base_type = graphene.NonNull(base_type)
    return graphene.List(base_type, description=field.help_text, required=not field.blank)


@_convert_db_field_to_argument.register(HStoreField)
@_convert_db_field_to_argument.register(JSONField)
def _(field):
    return JSONString(description=field.help_text, required=not field.blank)


@_convert_db_field_to_argument.register(forms.BooleanField)
def _(field):
    # Default `convert_form_field` always return required field.
    # https://github.com/graphql-python/graphene-django/issues/532
    return graphene.Boolean(
        description=field.help_text,
        required=field.required)
