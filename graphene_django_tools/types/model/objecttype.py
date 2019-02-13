"""Graphene types.  """

import graphene_django

from . import core


class ModelNode(graphene_django.DjangoObjectType):
    class Meta:
        abstract = True

    @classmethod
    def __init_subclass_with_meta__(
            cls,
            filterset_class=None,
            **options):
        # pylint: disable=W0221
        _meta = options.get('_meta', core.ModelNodeOptions(cls))
        _meta.filterset_class = filterset_class
        options['_meta'] = _meta
        super().__init_subclass_with_meta__(**options)
