Union
================


Iterable in schema that length greater than 1 and not match :doc:`/Enum` definition
will be parsed as union type.

Default name from current path and index.

Return value for union field should be mapping that contains ``__typename`` key.
``__typename`` value should be typename of one possible type.
Returns a graphene object type instance should also work but not tested.
