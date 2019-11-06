"""Utility.  """
from __future__ import annotations

import typing
from dataclasses import dataclass

import django.db.models
import graphene

from . import model_type


@dataclass
class ID:
    value: str
    type: str

    @classmethod
    def parse(cls, v: str) -> ID:
        """Parse graphene global id

        Args:
            v (str): value to parse

        Returns:
            ID: Parse result
        """
        type_, id_ = graphene.Node.from_global_id(v)
        return cls(
            value=id_,
            type=type_
        )

    def validate_type(
            self,
            expected: typing.Union[str, django.db.models.Model, graphene.Node]
    ) -> ID:
        """Validate if id match expected type.

        Args:
            expected (typing.Union[str, django.db.models.Model, graphene.Node]): type to match.

        Raises:
            ValueError: Type not match

        Returns:
            ID: self, for function chain.
        """
        # pylint:disable=protected-access
        if (isinstance(expected, type) and issubclass(expected, django.db.models.Model)):
            expected = model_type.get_model_typename(expected)
        if (isinstance(expected, type) and issubclass(expected, graphene.Node)):
            expected = expected._meta.name
        if self.type != expected:
            raise ValueError(
                f'Unexpected id type: expected={expected}, actual={self.type}.')
        return self


def convert_id(v, validate_type=None):
    """Convert global id values to local db id.

    Args:
        v: value(s) to convert.
        validate_type (optional): same as `ID.validate_type` args 1. Defaults to None.

    Returns:
        Converted values.
    """
    if not v:
        return v

    values = v
    is_list = not isinstance(v, str) and isinstance(v, typing.Iterable)
    if not is_list:
        values = [values]
    id_list = [ID.parse(i) for i in values]
    if validate_type is not None:
        _ = [i.validate_type(validate_type) for i in id_list]
    ret = [i.value for i in id_list]
    if not is_list:
        ret = ret[0]
    return ret
