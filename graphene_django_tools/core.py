"""Additional tools for `graphene_django`.  """
import sys
from typing import Type, Union

import django
import graphene
import graphene_django
from graphene.types.mountedtype import MountedType
from graphene.types.unmountedtype import UnmountedType
from graphene_django.registry import get_global_registry
from graphql import GraphQLError


def get_modelnode(model: Type[django.db.models.Model], is_autocreate=True)\
        -> Type[graphene_django.DjangoObjectType]:
    """Get graphene node class from model class.

    Args:
        model (Type[django.db.models.Model])
        is_autocreate (Boolean): Create modelnode type
            use default config if not created.

    Returns:
        Type[graphene_django.DjangoObjectType]
    """

    assert issubclass(model, django.db.models.Model), type(model)
    registry = get_global_registry()
    ret = registry.get_type_for_model(model)
    if ret:
        return ret
    if is_autocreate:
        return create_modelnode(model)
    raise RuntimeError(
        f'Defined node type first, or set `is_autocreate` to True: {model}')


def create_modelnode(model: Type[django.db.models.Model], bases=(), **meta_options) \
        -> Type[graphene_django.DjangoObjectType]:
    """Create node class for model class.

    Raises:
        AssertionError: node type already created.

    Returns:
        Type: Node type for model
    """

    assert issubclass(model, django.db.models.Model), type(model)

    from . import texttools
    meta_options.setdefault('model', model)
    meta_options.setdefault('interfaces', (graphene.Node,))
    meta_options.setdefault(
        'description', f'Auto created node type from model: {model.__name__}')
    if graphene_django.utils.DJANGO_FILTER_INSTALLED:
        meta_options.setdefault('filter_fields', '__all__')
    bases += (graphene_django.DjangoObjectType,)
    clsname = texttools.camel_case(f'{model.__name__}_node')
    return type(clsname, bases, dict(Meta=meta_options))


def handle_resolve_error():
    """Detail message for `graphql.error.located_error.GraphQLLocatedError`.  """

    type_, value, _ = sys.exc_info()
    if value is None:
        return
    if not isinstance(value, GraphQLError):
        import traceback
        traceback.print_exc()
        raise GraphQLError(f'{type_.__name__}:{value}')
    else:
        raise value


def get_node_id(instance: django.db.models.Model) -> str:
    """Get instance global node id.

    Args:
        instance (django.db.models.Model): Model instance

    Returns:
        str: Global id.
    """

    assert isinstance(instance, django.db.models.Model), type(instance)
    modelnode = get_modelnode(instance.__class__, is_autocreate=False)
    return graphene.Node.to_global_id(modelnode.__name__, instance.pk)


def get_unmounted_type(obj: Union[MountedType, UnmountedType]) -> UnmountedType:
    """Get unmounted type of given object object.

    Args:
        obj (Union[MountedType, UnmountedType]): Graphene object

    Returns:
        UnmountedType
    """

    unmounted = obj.type if isinstance(obj, MountedType) else obj
    if isinstance(unmounted, graphene.NonNull):
        unmounted = unmounted.of_type
    return unmounted
