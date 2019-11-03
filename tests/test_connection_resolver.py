# pylint:disable=missing-docstring,invalid-name
import graphene

import graphene_django_tools as gdtools


def test_simple():
    class Item(gdtools.Resolver):
        schema = {'name': 'String!'}

    class Items(gdtools.Resolver):
        schema = gdtools.get_connection(Item)

        def resolve(self, **kwargs):
            return gdtools.resolve_connection([{'name': 'a'}, {'name': 'b'}], **kwargs)

    class Query(graphene.ObjectType):
        items = Items.as_field()

    schema = graphene.Schema(query=Query)
    result = schema.execute('''\
{
    items{
        edges {
            node{
                name
            }
            cursor
        }
        pageInfo {
            total
            hasNextPage
            hasPreviousPage
            startCursor
            endCursor
        }
    }
}
''')
    assert not result.errors
    assert result.data == {
        "items": {
            "edges": [
                {"node": {"name": "a"}, "cursor": "YXJyYXljb25uZWN0aW9uOjA="},
                {"node": {"name": "b"}, "cursor": "YXJyYXljb25uZWN0aW9uOjE="}],
            "pageInfo": {
                "total": 2,
                "hasNextPage": False,
                "hasPreviousPage": False,
                "startCursor": "YXJyYXljb25uZWN0aW9uOjA=",
                "endCursor": "YXJyYXljb25uZWN0aW9uOjE="}},
    }
