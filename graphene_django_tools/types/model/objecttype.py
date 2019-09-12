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
        if hasattr(graphene_django.types.DjangoObjectTypeOptions, 'filterset_class'):
            # This attribute added in `graphene_django-2.4.0`
            options['filterset_class'] = filterset_class
        options['_meta'] = _meta
        super().__init_subclass_with_meta__(**options)
