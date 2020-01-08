"""Queryset optimization.  """

from __future__ import annotations
import logging
import typing

import django.db.models as djm
import graphql
import graphql.language.ast as ast_
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


LOGGER = logging.getLogger(__name__)
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


def _get_model_field(model: djm.Model, lookup: str) -> djm.Field:
    _model = model
    field = None
    for i in lookup.split('__'):
        field = _model._meta.get_field(i)
        _model = field.related_model
    assert field is not None
    return field


def _get_default_only_lookups(
        fieldname: str, model: djm.Model, related_query_name: str) -> typing.List[str]:
    field = None
    for lookup in (
            _format_related_name(related_query_name, fieldname),
            _format_related_name(related_query_name,
                                 phrases_case.snake(fieldname)),
    ):
        try:
            field = _get_model_field(model, lookup)
        except djm.FieldDoesNotExist:
            continue

    if field is None or field.many_to_many or field.one_to_many:
        return []

    return [field.name]


def _get_selection(ast: ast_.Node, fragments, is_recursive=True) -> typing.Iterator[ast_.Field]:
    if not is_recursive and isinstance(ast, ast_.Field):
        yield ast
        return
    if isinstance(ast, (ast_.Field, ast_.FragmentDefinition, ast_.InlineFragment)):
        for i in ast.selection_set and ast.selection_set.selections or []:
            yield from _get_selection(i, fragments, is_recursive=False)
    elif isinstance(ast, ast_.FragmentSpread):
        yield from _get_selection(fragments[ast.name.value], fragments)
    else:
        raise ValueError(f'Unknown ast type: {ast}')


def _format_related_name(related_query_name, name):
    if related_query_name is 'self':
        return name
    return f'{related_query_name}__{name}'


def _get_ast_optimization(ast, return_type, fragments, model, related_query_name='self') -> Optimization:

    inner_type = _get_inner_type(return_type)

    opt = get_optimization_option(inner_type.name)
    ret: Optimization = {
        'only': opt['only'].get(None, []),
        'select': opt['select'].get(None, []),
        'prefetch': opt['prefetch'].get(None, []),
    }

    for sub_ast in _get_selection(ast, fragments):
        fieldname = sub_ast.name.value
        ret['only'].extend(opt['only'].get(
            fieldname) or _get_default_only_lookups(fieldname, model, related_query_name))
        ret['select'].extend(opt['select'].get(fieldname, []))
        ret['prefetch'].extend(opt['prefetch'].get(fieldname, []))

        _related_query_name = opt['related'].get(fieldname)
        if not _related_query_name:
            continue
        _optimization = _get_ast_optimization(
            sub_ast,
            inner_type.fields[fieldname].type,
            fragments, model,
            _related_query_name
        )
        ret['only'].extend(_optimization['only'])
        ret['select'].extend(_optimization['select'])
        ret['prefetch'].extend(_optimization['prefetch'])

    ret['only'] = [_format_related_name(
        related_query_name, i) for i in ret['only']]
    ret['select'] = [_format_related_name(
        related_query_name, i) for i in ret['select']]
    ret['prefetch'] = [_format_related_name(
        related_query_name, i) for i in ret['prefetch']]
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
                i.name.value for i in _get_selection(ret[0], info.fragments)
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
    optimization = _get_ast_optimization(
        ast, return_type, info.fragments, queryset.model)
    LOGGER.debug("Optimization queryset: optimization=%s, model=%s",
                 optimization, queryset.model)
    qs = queryset
    if optimization['select']:
        qs = qs.select_related(*optimization['select'])
    if optimization['prefetch']:
        qs = qs.prefetch_related(*optimization['prefetch'])
    qs = qs.only(*optimization['only'], *optimization['select'])
    return qs
