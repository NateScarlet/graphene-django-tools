"""Field converter for django model.  """

import graphene
from django.db import models
from graphene_django.converter import convert_django_field

from ..core import get_modelnode


@convert_django_field.register(models.ManyToManyField)
@convert_django_field.register(models.ManyToManyRel)
@convert_django_field.register(models.ManyToOneRel)
def convert_field_to_list_or_connection(field, registry):
    from ..dataloader import DataLoaderModelFilterConnectionField, DataLoaderModelConnectionField, DataLoaderModelListField
    model = field.related_model

    def dynamic_type():
        # pylint: disable=protected-access
        _type = get_modelnode(model)
        if _type._meta.connection:
            if _type._meta.filter_fields:

                return DataLoaderModelFilterConnectionField(model)

            return DataLoaderModelConnectionField(model)

        return DataLoaderModelListField(model)

    return graphene.Dynamic(dynamic_type)


@convert_django_field.register(models.OneToOneRel)
def convert_one2one_field_to_djangomodel(field, registry=None):
    from ..dataloader import DataLoaderModelField
    model = field.related_model

    def dynamic_type():
        _type = registry.get_type_for_model(model)
        if not _type:
            return

        # We do this for a bug in Django 1.8, where null attr
        # is not available in the OneToOneRel instance
        null = getattr(field, "null", True)
        return DataLoaderModelField(model, required=not null)

    return graphene.Dynamic(dynamic_type)


@convert_django_field.register(models.OneToOneField)
@convert_django_field.register(models.ForeignKey)
def convert_field_to_djangomodel(field, registry=None):
    from ..dataloader import DataLoaderModelField
    model = field.related_model

    def dynamic_type():
        _type = registry.get_type_for_model(model)
        if not _type:
            return

        return DataLoaderModelField(model, description=field.help_text, required=not field.null)

    return graphene.Dynamic(dynamic_type)
