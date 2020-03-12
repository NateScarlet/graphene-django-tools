"""Process graphene global id.  """

from dataclasses import dataclass
from typing import Any, Iterable, List, Optional, Tuple, Union

import django.db.models as djm
import graphene

from . import model_type


@dataclass
class GlobalID:
    type: str
    value: str

    def __str__(self):
        return graphene.Node.to_global_id(self.type, self.value)

    def validate_type(
            self,
            expected: Union[str, Tuple[str, ...]]
    ) -> 'ID':
        """Validate if id match expected type.

        Args:
            expected: type name to match.

        Raises:
            ValueError: Type not match

        Returns:
            ID: self, for function chain.
        """

        expected_types = expected
        if not isinstance(expected_types, tuple):
            expected_types = (expected_types,)
        if self.type not in expected_types:
            raise ValueError(
                f'Unexpected id type: expected={expected}, actual={self.type}.')
        return self

    @classmethod
    def parse(cls, v: str) -> 'GlobalID':
        """Parse graphene global id

        Args:
            v (str): value to parse

        Returns:
            ID: Parse result
        """
        try:

            type_, id_ = graphene.Node.from_global_id(v)
        except (TypeError, ValueError) as ex:
            raise ValueError(f'Invalid id: value={v}') from ex
        return cls(
            value=id_,
            type=type_
        )

    @classmethod
    def from_object(cls, obj: djm.Model) -> str:
        """Get global id from db model object.

        Args:
            obj (djm.Model): Object.

        Returns:
            str: Global id.
        """
        typename = model_type.get_typename(obj._meta.model)

        return cls(type=typename, value=str(obj.pk))

    @classmethod
    def cast(cls, value: Any) -> 'GlobalID':
        """Convert unknown value to global id.

        Args:
            Any (Any): Value

        Raises:
            ValueError: Invalid value.

        Returns:
            GlobalID: cas result.
        """

        if isinstance(value, str):
            return cls.parse(value)
        if isinstance(value, djm.Model):
            return cls.from_object(value)

        raise ValueError(f"Can not cast value to global id: {repr(value)}")

    @classmethod
    def convert(
            cls,
            v: Any,
            validate_type: Union[str, Tuple[str, ...]] = None
    ) -> Optional[Union['GlobalID', List['GlobalID']]]:
        """Convert global id values to local db id.

        Args:
            v: value(s) to convert.
            validate_type (optional): same as `ID.validate_type` args 1. Defaults to None.

        Returns:
            Converted values.
        """
        if v is None:
            return v

        values = v
        is_list = not isinstance(v, str) and isinstance(v, Iterable)
        if not is_list:
            values = [values]
        id_list = [cls.cast(i) for i in values]
        if validate_type is not None:
            _ = [i.validate_type(validate_type) for i in id_list]
        ret = [i.value for i in id_list]
        if not is_list:
            ret = ret[0]
        return ret
