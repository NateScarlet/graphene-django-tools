from django.contrib import admin
from django.urls import include, path
from django.views.decorators.csrf import csrf_exempt
from graphene_django.views import GraphQLView

from .schema import SCHEMA

app_name = 'api'
urlpatterns = [
    path('', csrf_exempt(GraphQLView.as_view(graphiql=True, schema=SCHEMA)))
]
