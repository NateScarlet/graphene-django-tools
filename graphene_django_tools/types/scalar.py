"""Graphene scalar types.  """

from datetime import timedelta

import graphene
import isodate
from graphql.language import ast


class Duration(graphene.Scalar):
    """Duration in ISO-8601 format.  """

    @staticmethod
    def serialize(duration: timedelta):
        """Serialize python object.

        Args:
            duration (timedelta): Duration

        Returns:
            str
        """

        return isodate.duration_isoformat(duration)

    @classmethod
    def parse_literal(cls, node):
        """Parse ast node.

        Args:
            node: AST node

        Returns:
            timedelta | None
        """

        if isinstance(node, ast.StringValue):
            return cls.parse_value(node.value)
        return None

    @staticmethod
    def parse_value(value):
        """Parse str to python object.

        Args:
            value (str): Value

        Returns:
            timedelta | None
        """

        try:
            return isodate.parse_duration(value)
        except ValueError:
            return None
