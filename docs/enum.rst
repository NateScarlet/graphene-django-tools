Enum
=====================

Use iterable that all items is string or 2-value tuple to define enum type.
when using tuple, first tuple item used as enum value, second tuple item used as description.

When length be 1, schema will be parsed as list type.
Use ``graphene.Enum`` for enum that only has one possible value if you really need.
