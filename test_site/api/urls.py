from django.contrib import admin
from django.urls import include, path
from graphene_django.views import GraphQLView

from .schema import SCHEMA

app_name = 'api'
urlpatterns = [
    path('', GraphQLView.as_view(graphiql=True, schema=SCHEMA))
]
