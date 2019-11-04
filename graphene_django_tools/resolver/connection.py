"""Relay compatible connection resolver.  """
import typing

import graphene_django.fields as _gd_impl
from graphql_relay.connection import arrayconnection

from . import resolver
from . import schema as schema_

CONNECTION_REGISTRY: typing.Dict[str, typing.Type] = {}


class PageInfo(resolver.Resolver):
    """Connection page info resolver.  """

    schema = {
        'name': 'PageInfoV2',  # Avoid name conflict with graphene page info.
        'type': {
            'hasNextPage': {
                'type': 'Boolean!',
                'description': 'When paginating forwards, are there more items?'
            },
            'hasPreviousPage': {
                'type': 'Boolean!',
                'description': 'When paginating backwards, are there more items?'
            },
            'startCursor': {
                'type': 'String',
                'description': 'When paginating backwards, the cursor to continue.'
            },
            'endCursor': {
                'type': 'String',
                'description': 'When paginating forwards, the cursor to continue.'
            },
            'total': {
                'type': 'Int!',
                'description': 'Total item count in connection.'
            }
        },
        'description': ("The Relay compliant `PageInfo` type, containing data necessary to"
                        " paginate this connection.")
    }


def get_connection(
        node: typing.Union[resolver.Resolver, str, typing.Any],
        *,
        page_info=PageInfo,
        name: str = None,
) -> resolver.Resolver:
    """Get connection resolver.

    Args:
        node (typing.Union[resolver.Resolver, str, typing.Any]): Node resolver or schema.
        page_info (typing.Union[resolver.Resolver, typing.Any], optional):
            Page resolver or schema, defaults to PageInfo.
        name (str, optional): Override default connection name, required no node name not defined.

    Returns:
        resolver.Resolver: Created connection resolver, same name will returns same resolver.
    """

    def _get_node_name() -> str:
        if isinstance(node, str):
            return node
        if (isinstance(node, type)
                and issubclass(node, resolver.Resolver)):
            node_name = schema_.FieldDefinition.parse(
                node.schema, default={'name': node.__name__}).name
        else:
            node_name = schema_.FieldDefinition.parse(node).name
        return node_name
    name = name or f'{_get_node_name()}Connection'

    if name not in CONNECTION_REGISTRY:
        CONNECTION_REGISTRY[name] = type(name, (resolver.Resolver,), dict(schema=dict(
            name=name,
            args=dict(
                first='Int',
                last='Int',
                before='String',
                after='String',
            ),
            type={
                'pageInfo': page_info,
                'edges': [{
                    'name': f'{name}Edge',
                    'type': {
                        'node': {
                            'type': node,
                            'description': 'The item at the end of the edge',
                        },
                        'cursor': {
                            'type': 'String!',
                            'description': 'A cursor for use in pagination'
                        },
                    }
                }]
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

    edges = [
        dict(
            node=node,
            cursor=arrayconnection.offset_to_cursor(start_offset + i)
        )
        for i, node in enumerate(iterable[start_offset:end_offset])
    ]

    return dict(
        edges=edges,
        pageInfo=dict(
            startCursor=edges[0]['cursor'] if edges else None,
            endCursor=edges[-1]['cursor'] if edges else None,
            hasPreviousPage=isinstance(
                last, int) and start_offset > (after_offset + 1 if after else 0),
            hasNextPage=isinstance(
                first, int) and end_offset < (before_offset if before else _len),
            total=_len,
        )
    )
