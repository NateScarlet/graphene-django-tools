"""Relay compatible connection resolver.  """
import re
import typing

import graphene
import graphene_django.fields as _gd_impl
from graphql_relay.connection import arrayconnection

from . import resolver
from . import schema as schema_

CONNECTION_REGISTRY: typing.Dict[str, typing.Type] = {}


def _get_node_name(node: typing.Union[resolver.Resolver, str, typing.Any]) -> str:
    if isinstance(node, str):
        return node
    if (isinstance(node, type)
            and issubclass(node, resolver.Resolver)):
        node_name = schema_.FieldDefinition.parse(
            node.schema, default={'name': node.__name__}).name
    else:
        node_name = schema_.FieldDefinition.parse(node).name
    return node_name


def get_connection(
        node: typing.Union[resolver.Resolver, str, typing.Any],
        *,
        name: str = None,
) -> resolver.Resolver:
    """Get a github-like connection resolver. see at https://developer.github.com/v4/explorer/

    Args:
        node (typing.Union[resolver.Resolver, str, typing.Any]): Node resolver or schema.
        page_info (typing.Union[resolver.Resolver, typing.Any], optional):
            Page resolver or schema, defaults to PageInfo.
        name (str, optional): Override default connection name,
            required when node name is not defined.

    Returns:
        resolver.Resolver: Created connection resolver, same name will returns same resolver.
    """

    name = name or f'{_get_node_name(node)}Connection'

    if name in CONNECTION_REGISTRY:
        return CONNECTION_REGISTRY[name]

    edge_name = f"{re.sub('Connection$', '', name)}Edge"
    CONNECTION_REGISTRY[name] = type(name, (resolver.Resolver,), dict(schema=dict(
        name=name,
        description=f"The connection type for {re.sub('Connection$', '', name)}.",
        args=dict(
            after={
                'type': 'String',
                'description': ('Returns the elements in the list '
                                'that come after the specified cursor.')
            },
            before={
                'type': 'String',
                'description': ('Returns the elements in the list '
                                'that come before the specified cursor.')
            },
            first={
                'type': 'Int',
                'description': 'Returns the first _n_ elements from the list.'
            },
            last={
                'type': 'Int',
                'description': 'Returns the last _n_ elements from the list.'
            },
        ),
        type={
            'edges': {
                'type': [{
                    'name': edge_name,
                    'type': {
                        'node': {
                            'type': node,
                            'description': 'The item at the end of the edge.',
                        },
                        'cursor': {
                            'type': 'String!',
                            'description': 'A cursor for use in pagination.'
                        },
                    },
                }],
                'description': 'A list of edges.'
            },
            'nodes': {
                'type': [node],
                'description': 'A list of nodes.'
            },
            'pageInfo': {
                'type': graphene.relay.PageInfo,
                'required': True,
                'description': 'Information to aid in pagination.',
            },
            'totalCount': {
                'type': 'Int!',
                'description': 'Identifies the total count of items in the connection.',
            },
        }
    )))

    return CONNECTION_REGISTRY[name]


def resolve_connection(
        iterable,
        *,
        first: int = None,
        last: int = None,
        after: str = None,
        before: str = None,
        **_,
) -> dict:
    """Resolve iterable to connection

    Args:
        iterable (typign.Iterable): value

    Returns:
        dict: Connection data.
    """
    iterable = _gd_impl.maybe_queryset(iterable)
    if isinstance(iterable, _gd_impl.QuerySet):
        _len = iterable.count()
    else:
        _len = len(iterable)

    before_offset = arrayconnection.get_offset_with_default(before, _len)
    after_offset = arrayconnection.get_offset_with_default(after, -1)
    start_offset = max(after_offset, -1) + 1
    end_offset = min(before_offset, _len)
    if isinstance(first, int):
        end_offset = min(end_offset, start_offset + first)
    if isinstance(last, int):
        start_offset = max(start_offset, end_offset - last)

    nodes = list(iterable[start_offset:end_offset])
    edges = [
        dict(
            node=node,
            cursor=arrayconnection.offset_to_cursor(start_offset + i)
        )
        for i, node in enumerate(nodes)
    ]

    return dict(
        nodes=nodes,
        edges=edges,
        pageInfo=dict(
            start_cursor=edges[0]['cursor'] if edges else None,
            end_cursor=edges[-1]['cursor'] if edges else None,
            has_previous_page=isinstance(
                last, int) and start_offset > (after_offset + 1 if after else 0),
            has_next_page=isinstance(
                first, int) and end_offset < (before_offset if before else _len),
        ),
        totalCount=_len,
    )
