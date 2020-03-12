
import django.http as http
import graphene
import pytest
# pylint:disable=missing-docstring,invalid-name,unused-variable
from django.utils import timezone

import graphene_django_tools as gdtools

from . import models

pytestmark = [pytest.mark.django_db]


def test_simple(django_assert_num_queries):
    reporter1 = models.Reporter.objects.create(
        first_name='reporter1',
    )
    reporter2 = models.Reporter.objects.create(
        first_name='reporter2',
    )

    class Reporter(gdtools.Resolver):
        schema = {
            'type': {'first_name': 'String!'},
        }
        model = models.Reporter

    class GetReporter(gdtools.Resolver):
        schema = {
            'args': {
                'id': 'ID'
            },
            'type': 'Reporter'
        }

        def resolve(self, **kwargs):
            return self.resolve_gid(kwargs['id'])

    class Query(graphene.ObjectType):
        get_reporter = GetReporter.as_field()

    schema = graphene.Schema(
        query=Query,
    )
    with django_assert_num_queries(1):
        result = schema.execute(
            '''\
query getReporters($id1: ID, $id2: ID){
    reporter1: getReporter(id: $id1) {
        firstName
    }
    reporter2: getReporter(id: $id2) {
        firstName
    }
}
''',
            context=http.HttpRequest(),
            variables={
                'id1': gdtools.GlobalID.from_object(reporter1),
                'id2': gdtools.GlobalID.from_object(reporter2),
            }
        )
        assert not result.errors
        assert result.data == {
            'reporter1': {
                'firstName': 'reporter1'
            },
            'reporter2': {
                'firstName': 'reporter2'
            }
        }
