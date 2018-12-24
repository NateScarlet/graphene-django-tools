"""Convert django field to graphene field.  """

from typing import Optional

import django
import graphene
from graphene_django import converter as _converter
from graphene_django.registry import Registry

from ..texttools import camel_case


def construct_enum_from_db_field(field, registry: Optional[Registry] = None):
    """Construct enum field from django db field.

    Args:
        field (django.db.models.Field): Field
        registry (Optional[Registry], optional): Defaults to None. Field registry

    Returns:
        graphene.Enum: Enum field.
    """

    if registry:
        converted = registry.get_converted_field(field)
        if converted:
            return converted
    meta: django.db.models.options.Options = field.model._meta
    name = camel_case("{}_{}".format(meta.object_name, field.name))
    choices = list(_converter.get_choices(field.choices))
    named_choices = [(c[0], c[1]) for c in choices]
    named_choices_descriptions = {c[0]: c[2] for c in choices}

    class EnumWithDescriptionsType(object):
        # pylint:disable=all
        @property
        def description(self):
            return named_choices_descriptions[self.name]

    enum = graphene.Enum(name, list(named_choices),
                         type=EnumWithDescriptionsType)
    converted = enum(description=field.help_text, required=not field.null)
    if registry:
        registry.register_converted_field(field, converted)
