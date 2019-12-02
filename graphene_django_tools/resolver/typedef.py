# -*- coding=UTF-8 -*-
"""Mongoose-like schema.  """

#pylint: disable=invalid-name

from __future__ import annotations
import typing

import graphene
from graphene_resolver import typedef as typedef_
from graphene_resolver.typedef import *  # pylint:disable=wildcard-import,unused-wildcard-import

GRAPHENE_TYPE_REGISTRY: typing.Dict[
    str,
    typing.Type[graphene.types.unmountedtype.UnmountedType]
] = typedef_.REGISTRY


dynamic_type = typedef_.dynamic_type
