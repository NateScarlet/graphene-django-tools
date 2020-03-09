# pylint:disable=missing-docstring,invalid-name,unused-variable

from django.utils import timezone
import graphene
import pytest

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

    class Article(gdtools.Resolver):
        schema = {'headline': 'String!', 'reporter': 'Reporter!'}

    class Articles(gdtools.Resolver):
        schema = ['Article!']

        def resolve(self, **kwargs):
            qs = models.Article.objects.all()
            return gdtools.queryset.optimize(qs, self.info)

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
            headline
            reporter{
                firstName
            }
        }
    }
    ''')
        assert not result.errors
        assert result.data == {
            "articles": [
                {
                    "headline": "article1",
                    "reporter": {
                        "firstName": "reporter1"
                    }
                }
            ]
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

    class Article(gdtools.Resolver):
        schema = {'headline': 'String!', 'reporter': 'Reporter!'}

    class Articles(gdtools.Resolver):
        schema = ['Article!']

        def resolve(self, **kwargs):
            qs = models.Article.objects.all()
            return gdtools.queryset.optimize(qs, self.info)

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
    ''')
        assert not result.errors
        assert result.data == {
            'articles':  [{
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

    class Article(gdtools.Resolver):
        schema = {'headline': 'String!', 'reporter': 'Reporter!'}

    class Articles(gdtools.Resolver):
        schema = ['Article!']

        def resolve(self, **kwargs):
            qs = models.Article.objects.all()
            return gdtools.queryset.optimize(qs, self.info)

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
            headline
            reporter{
                __typename
                firstName
            }
        }
    }
    ''')
        assert not result.errors
        assert result.data == {
            'articles': [
                {
                    'headline': 'article1',
                    'reporter': {'firstName': 'reporter1', '__typename': 'Reporter'}
                }
            ]
        }


@pytest.mark.django_db
def test_fragment_spread(django_assert_num_queries):
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

    class Article(gdtools.Resolver):
        schema = {'headline': 'String!', 'reporter': 'Reporter!'}

    class Articles(gdtools.Resolver):
        schema = ['Article!']

        def resolve(self, **kwargs):
            qs = models.Article.objects.all()
            return gdtools.queryset.optimize(qs, self.info)

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
            ...ArticleFields
            headline
        }
    }
    fragment ArticleFields on Article {
        
        reporter{
            firstName
        }
    }
    ''')
        assert not result.errors
        assert result.data == {
            "articles": [
                {
                    "headline": "article1",
                    "reporter": {
                        "firstName": "reporter1"
                    }
                }
            ]
        }


@pytest.mark.django_db
def test_inline_fragment(django_assert_num_queries):
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

    class Article(gdtools.Resolver):
        schema = {'headline': 'String!', 'reporter': 'Reporter!'}

    class Articles(gdtools.Resolver):
        schema = ['Article!']

        def resolve(self, **kwargs):
            qs = models.Article.objects.all()
            return gdtools.queryset.optimize(qs, self.info)

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
            headline
            ...  on Article {   
                reporter{
                    firstName
                }
            }
        }
    }
    ''')
        assert not result.errors
        assert result.data == {
            "articles": [
                {
                    "headline": "article1",
                    "reporter": {
                        "firstName": "reporter1"
                    }
                }
            ]
        }


@pytest.mark.django_db
def test_m2m_default_only():
    reporter = models.Reporter.objects.create(
        first_name='reporter1',
        last_name='test',
        email='user@example.com',
        a_choice=1,

    )
    film = models.Film.objects.create()
    film.reporters.add(reporter)

    class Reporter(gdtools.Resolver):
        schema = {
            'first_name': 'String!'
        }

    class FilmReporters(gdtools.Resolver):
        schema = ['Reporter!']

        def resolve(self, **kwargs):
            return self.parent.reporters.all()

    class Film(gdtools.Resolver):
        schema = {'reporters': FilmReporters}

    class Films(gdtools.Resolver):
        schema = ['Film!']

        def resolve(self, **kwargs):
            qs = models.Film.objects.all()
            return gdtools.queryset.optimize(qs, self.info)

    class Query(graphene.ObjectType):
        films = Films.as_field()
    schema = graphene.Schema(query=Query)

    result = schema.execute('''\
{
    films{
        reporters{
            firstName
        }
    }
}
''')
    assert not result.errors
    assert result.data == {
        'films': [{
            "reporters": [
                {
                    "firstName": "reporter1"
                }
            ]
        }]
    }


@pytest.mark.django_db
def test_generic_foreign_key_default_only():
    reporter = models.Reporter.objects.create(
        first_name='reporter1',
        last_name='test',
        email='user@example.com',
        a_choice=1,

    )
    film = models.Film.objects.create()
    models.Tag.objects.create(
        content=film,
        name='test'
    )

    class Film(gdtools.Resolver):
        schema = {
            'genre': 'String!'
        }

    class Tag(gdtools.Resolver):
        schema = {'content': 'Film'}

    class Tags(gdtools.Resolver):
        schema = ['Tag!']

        def resolve(self, **kwargs):
            qs = models.Tag.objects.all()
            return gdtools.queryset.optimize(qs, self.info)

    class Query(graphene.ObjectType):
        tags = Tags.as_field()
    schema = graphene.Schema(query=Query)

    result = schema.execute('''\
{
    tags{
        content{
            genre
        }
    }
}
''')
    assert not result.errors
    assert result.data == {
        'tags': [{
            "content": {"genre": "ot"}
        }]
    }
