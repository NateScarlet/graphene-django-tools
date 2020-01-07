"""Queryset optimization.  """

from __future__ import annotations
import typing

import django.db.models as djm
import graphql
import phrases_case

if typing.TYPE_CHECKING:
    class OptimizationOption(typing.TypedDict):
        """
        Optimization option dict.
        See :doc:`/optimize` for more information.  
        """

        only: typing.Dict[typing.Optional[str], typing.List[str]]
        select: typing.Dict[typing.Optional[str], typing.List[str]]
        prefetch: typing.Dict[typing.Optional[str], typing.List[str]]
        related: typing.Dict[str, str]

    class Optimization(typing.TypedDict):
        """Optimization computation result dict.  """

        only: typing.List[str]
        select: typing.List[str]
        prefetch: typing.List[str]


OPTIMIZATION_OPTIONS: typing.Dict[str, dict] = {}


def get_optimization_option(typename: str) -> OptimizationOption:
    """Get optimization options from typename.

    Args:
        typename (str): Graphql typename.

    Returns:
        OptimizationOption: Options.
    """

    ret = OPTIMIZATION_OPTIONS.get(
        typename,
        {},
    )
    ret.setdefault('only', {})  # type: ignore
    ret.setdefault('select', {})  # type: ignore
    ret.setdefault('prefetch', {})  # type: ignore
    ret.setdefault('related', {})  # type: ignore
    return ret  # type: ignore


def _get_inner_type(return_type):
    if not hasattr(return_type, 'of_type'):
        return return_type
    return _get_inner_type(return_type.of_type)


def _get_default_only(fieldname: str) -> typing.List[str]:
    if fieldname.startswith('__'):
        # Graphql special field.
        return []

    return [phrases_case.snake(fieldname)]


def _get_ast_optimization(ast, return_type) -> Optimization:
    def _format_related_name(related_query_name, name):
        if related_query_name is True:
            return name
        return f'{related_query_name}__{name}'
    inner_type = _get_inner_type(return_type)

    opt = get_optimization_option(inner_type.name)
    ret: Optimization = {
        'only': opt['only'].get(None, []),
        'select': opt['select'].get(None, []),
        'prefetch': opt['prefetch'].get(None, []),
    }
    for sub_ast in ast.selection_set.selections:
        fieldname = sub_ast.name.value
        ret['only'].extend(opt['only'].get(
            fieldname, _get_default_only(fieldname)))
        ret['select'].extend(opt['select'].get(fieldname, []))
        ret['prefetch'].extend(opt['prefetch'].get(fieldname, []))
        related_query_name = opt['related'].get(fieldname)
        if not related_query_name:
            continue
        _optimization = _get_ast_optimization(
            sub_ast, inner_type.fields[sub_ast.name.value].type)
        ret['only'].extend([_format_related_name(related_query_name, i)
                            for i in _optimization['only']])
        ret['select'].extend([_format_related_name(
            related_query_name, i) for i in _optimization['select']])
        ret['prefetch'].extend([_format_related_name(
            related_query_name, i) for i in _optimization['prefetch']])
    return ret


def _get_ast_and_return_type(
        info: graphql.ResolverInfo,
        path: typing.Optional[typing.List[str]]
) -> typing.Tuple[graphql.GraphQLField, typing.Union[
    graphql.GraphQLList,
    graphql.GraphQLObjectType,
    graphql.GraphQLScalarType
]]:
    ret = (info.field_asts[0], info.return_type)
    for fieldname in path or []:
        ret = (
            next(
                i.name.value for i in ret[0].selection_set.selections
                if i.name.value == fieldname
            ),
            ret[1].fields[fieldname]
        )
    return ret


def optimize(
        queryset: djm.QuerySet,
        info: graphql.ResolveInfo,
        path: typing.Optional[typing.List[str]] = None
) -> djm.QuerySet:
    """Optimization queryset with resolve info and global optimization options.

    Args:
        info (graphql.ResolveInfo): Resolve info.
        queryset (djm.QuerySet): Queryset to optimize.
        path (typing.Optional[typing.List[str]]): Field path. defaults to None.
            None means root field.

    Returns:
        djm.QuerySet: optimized queryset.
    """

    ast, return_type = _get_ast_and_return_type(info, path)
    optimization = _get_ast_optimization(ast, return_type)
    print(optimization)
    qs = queryset
    if optimization['select']:
        qs = qs.select_related(*optimization['select'])
    if optimization['prefetch']:
        qs = qs.prefetch_related(*optimization['prefetch'])
    qs = qs.only(*optimization['only'])
    return qs
