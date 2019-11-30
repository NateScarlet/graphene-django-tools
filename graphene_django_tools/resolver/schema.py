# -*- coding=UTF-8 -*-
"""Mongoose-like schema.  """
# pylint:disable=unused-import

from __future__ import annotations

import django.db.models
import graphene_django.converter
import graphene_django.registry

import graphene_resolver
from graphene_resolver.schema import *  # pylint:disable=wildcard-import,unused-wildcard-import


@graphene_resolver.CONFIG_PROCESSOR.register(110)
def _process_django_field(type_def, config):
    if not isinstance(type_def, django.db.models.Field):
        return None
    config['type'] = graphene_django.converter.convert_django_field_with_choices(
        type_def,
        registry=graphene_django.registry.get_global_registry()).__class__
    return dict(
        config=config
    )
