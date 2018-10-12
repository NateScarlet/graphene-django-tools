"""GrapQl schema.  """

import graphene
import graphene_django
from django.contrib.auth.models import User

import graphene_django_tools as gdtools
from graphene_django_tools import auth


class Mutation(graphene.ObjectType):
    """Mutation """

    create_user = auth.UserCreation.Field()
    update_user = auth.UserUpdate.Field()
    login = auth.Login.Field()
    logout = auth.Logout.Field()


class Query(graphene.ObjectType):
    """Query"""
    user = gdtools.ModelField(auth.User)


SCHEMA = graphene.Schema(
    query=Query,
    mutation=Mutation,
    auto_camelcase=False)
