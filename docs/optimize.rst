Optimize
======================

We can use resolve info to optimize django queryset with ``queryset.optimize``.

For connection, there is a `connection.optimized_resolve` shortcut function.

Before use these function, `queryset.OPTIMIZE_OPTIONS` for corresponding graphql type is required.

example:

```python
    class Reporter(gdtools.Resolver):
        schema = {
            'first_name': 'String!'
        }

    class Article(gdtools.Resolver):
        schema = {'headline': 'String!', 'reporter': 'Reporter!'}

    class Articles(gdtools.Resolver):
        schema = gdtools.get_connection(Article)

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
```


OptimizeOption
-----------------------

A dict contains optimize information.

items:

only

  a map use graphql field name as key, django queryset ``only`` lookup list as value.
  
  ``queryset.optimize`` will use all lookup that field appeared in graphql query.

  lookups that key is ``None`` always used.

select

  a map use graphql field name as key, django queryset ``select_related`` lookup list as value.
  
  ``queryset.optimize`` will use all lookup that field appeared in graphql query.

  lookups that key is ``None`` always used.

prefetch

  a map use graphql field name as key, django queryset ``prefetch__related`` lookup list as value.
  
  ``queryset.optimize`` will use all lookup that field appeared in graphql query.

  lookups that key is ``None`` always used.

related

  a map use graphql field name as key, django related query name as value.
  
  ``queryset.optimize`` will use collect OptimizeOption for that field when field appeared in graphql query then
  
  merge it to current option with django related query syntax.

  When value is ``"self"``, sub OptimizeOption will merge to current option directly.


