"""Relay compatible connection resolver.  """

import graphene_django.fields as _gd_impl
from graphql_relay.connection import arrayconnection

from . import resolver


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

    def resolve(self, **kwargs):
        return self.parent['pageInfo']


class ConnectionResolver(resolver.Resolver):
    """Connection resolver with a `resolve_connection` shortcut method.  """

    def __init_subclass__(cls):
        if not cls.schema:
            raise NotImplementedError(
                f'Resolver schema is not defined: {cls.__name__}')

        node_def = cls.schema.get('node')
        if not node_def:
            raise NotImplementedError(
                f'Node schema is not defined: {cls.__name__}')
        cls.schema.setdefault('name', cls.__name__)
        cls.schema.setdefault('args', {})
        cls.schema.get('args').update(
            first='Int',
            last='Int',
            before='String',
            after='String',
        )
        cls.schema.update(
            type={
                'pageInfo': cls.schema.get('pageInfo', PageInfo),
                'edges': [{
                    'name': f'{cls.__name__}Edge',
                    'type': {
                        'node': {
                            'type': node_def,
                            'description': 'The item at the end of the edge',
                        },
                        'cursor': {
                            'type': 'String!',
                            'description': 'A cursor for use in pagination'
                        },
                    }
                }]
            })

    def resolve_connection(
            self,
            iterable,
            *,
            first: int = None,
            last: int = None,
            after: str = None,
            before: str = None
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
