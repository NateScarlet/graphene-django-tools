# pylint:disable=missing-docstring,invalid-name,unused-variable
import django.http as http
import graphene
import pytest
from django.utils import timezone

import graphene_django_tools as gdtools

from . import models


@pytest.mark.django_db
def test_query_select_related(django_assert_num_queries):
    reporter = models.Reporter.objects.create(
        first_name='reporter1',
        last_name='test',
        email='user@example.com',
        a_choice=1,

    )
    models.Article.objects.create(
        headline='article1',
        pub_date=timezone.now(),
        pub_date_time=timezone.now(),
        reporter=reporter,
        editor=reporter,
    )

    class Reporter(gdtools.Resolver):
        schema = {
            'first_name': 'String!'
        }
        model = models.Reporter

    class Article(gdtools.Resolver):
        schema = {'headline': 'String!', 'reporter': 'Reporter!'}
        model = models.Article

    class Articles(gdtools.Resolver):
        schema = gdtools.connection.get_type(Article)

        def resolve(self, **kwargs):
            qs = models.Article.objects.all()
            return gdtools.connection.optimized_resolve(self.info, qs, **kwargs)

    class Query(graphene.ObjectType):
        articles = Articles.as_field()
    schema = graphene.Schema(query=Query)
    gdtools.queryset.OPTIMIZATION_OPTIONS['Article'] = {
        'select': {'reporter': ['reporter']},
        'related': {'reporter': 'reporter'},
    }
    gdtools.queryset.OPTIMIZATION_OPTIONS['Reporter'] = {
        'only': {None: ['reporter_type']},
    }

    with django_assert_num_queries(1):
        result = schema.execute('''\
    {
        articles{
            nodes {
                headline
                reporter{
                    firstName
                }
            }
            edges {
                node {
                    headline
                }
                cursor
            }
            pageInfo {
                startCursor
                endCursor
            }
        }
    }
    ''', context=http.HttpRequest())
        assert not result.errors
        assert result.data == {
            "articles": {
                "nodes": [
                    {
                        "headline": "article1",
                        "reporter": {
                            "firstName": "reporter1"
                        }
                    }
                ],
                "edges": [
                    {
                        "node": {
                            "headline": "article1"
                        },
                        "cursor": "YXJyYXljb25uZWN0aW9uOjA="
                    }
                ],
                "pageInfo": {
                    "startCursor": "YXJyYXljb25uZWN0aW9uOjA=",
                    "endCursor": "YXJyYXljb25uZWN0aW9uOjA="
                }
            }
        }


@pytest.mark.django_db
def test_query_prefetch_related(django_assert_num_queries):
    reporter1 = models.Reporter.objects.create(
        first_name='reporter1',
        last_name='test',
        email='user@example.com',
        a_choice=1,
    )
    reporter2 = models.Reporter.objects.create(
        first_name='reporter2',
        last_name='test',
        email='user@example.com',
        a_choice=1,
    )
    reporter3 = models.Reporter.objects.create(
        first_name='reporter3',
        last_name='test',
        email='user@example.com',
        a_choice=1,
    )
    reporter1.friends.add(reporter2, reporter3)
    models.Article.objects.create(
        headline='article1',
        pub_date=timezone.now(),
        pub_date_time=timezone.now(),
        reporter=reporter1,
        editor=reporter2,
    )

    class ReporterFriends(gdtools.Resolver):
        schema = ['Reporter!']

        def resolve(self, **kwargs):
            return self.parent.friends.all()

    class Reporter(gdtools.Resolver):
        schema = {
            'first_name': 'String!',
            'friends': ReporterFriends
        }
        model = models.Reporter

    class Article(gdtools.Resolver):
        schema = {'headline': 'String!', 'reporter': 'Reporter!'}
        model = models.Article

    class Articles(gdtools.Resolver):
        schema = gdtools.connection.get_type(Article)

        def resolve(self, **kwargs):
            qs = models.Article.objects.all()
            return gdtools.connection.optimized_resolve(self.info, qs, **kwargs)

    class Query(graphene.ObjectType):
        articles = Articles.as_field()
    schema = graphene.Schema(query=Query)
    gdtools.queryset.OPTIMIZATION_OPTIONS['Article'] = {
        'select': {'reporter': ['reporter']},
        'related': {'reporter': 'reporter'},
    }
    gdtools.queryset.OPTIMIZATION_OPTIONS['Reporter'] = {
        'only': {None: ['reporter_type']},
        'prefetch': {'friends': ['friends']},
        'related': {'friends': 'friends'},
    }

    # will be 4 query if not using prefetch.
    with django_assert_num_queries(3):
        result = schema.execute('''\
    {
        articles{
            nodes {
                headline
                reporter{
                    firstName
                    friends{
                        firstName
                        friends {
                            firstName
                        }
                    }
                }
            }
        }
    }
    ''',  context=http.HttpRequest())
        assert not result.errors
        assert result.data == {
            'articles': {
                'nodes': [{
                    'headline': 'article1',
                    'reporter': {
                        'firstName': 'reporter1',
                        'friends': [
                            {
                                'firstName': 'reporter2',
                                'friends': [{'firstName': 'reporter1'}]
                            },
                            {
                                'firstName': 'reporter3',
                                'friends': [{'firstName': 'reporter1'}]
                            }
                        ]
                    }
                }]
            }
        }


@pytest.mark.django_db
def test_query_special_field(django_assert_num_queries):
    reporter = models.Reporter.objects.create(
        first_name='reporter1',
        last_name='test',
        email='user@example.com',
        a_choice=1,

    )
    models.Article.objects.create(
        headline='article1',
        pub_date=timezone.now(),
        pub_date_time=timezone.now(),
        reporter=reporter,
        editor=reporter,
    )

    class Reporter(gdtools.Resolver):
        schema = {
            'first_name': 'String!'
        }
        model = models.Reporter

    class Article(gdtools.Resolver):
        schema = {'headline': 'String!', 'reporter': 'Reporter!'}
        model = models.Article

    class Articles(gdtools.Resolver):
        schema = gdtools.connection.get_type(Article)

        def resolve(self, **kwargs):
            qs = models.Article.objects.all()
            return gdtools.connection.optimized_resolve(self.info, qs, **kwargs)

    class Query(graphene.ObjectType):
        articles = Articles.as_field()
    schema = graphene.Schema(query=Query)
    gdtools.queryset.OPTIMIZATION_OPTIONS['Article'] = {
        'select': {'reporter': ['reporter']},
        'related': {'reporter': 'reporter'},
    }
    gdtools.queryset.OPTIMIZATION_OPTIONS['Reporter'] = {
        'only': {None: ['reporter_type']},
    }

    with django_assert_num_queries(1):
        result = schema.execute(
            '''\
    {
        articles{
            nodes {
                headline
                reporter{
                    __typename
                    firstName
                }
            }
        }
    }
    ''',
            context=http.HttpRequest()
        )
        assert not result.errors
        assert result.data == {
            'articles': {
                'nodes': [
                    {
                        'headline': 'article1',
                        'reporter': {'firstName': 'reporter1', '__typename': 'Reporter'}
                    }
                ]
            }
        }
