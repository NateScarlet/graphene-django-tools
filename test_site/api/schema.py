"""GrapQl schema.  """

import graphene
from django.contrib.auth.models import User
from graphene import relay
from graphene_django import DjangoObjectType

import graphene_django_tools as gdtools
from graphene_django_tools import auth


class UserNode(DjangoObjectType):
    class Meta:
        model = User
        filter_fields = {
            'username': ['icontains', 'istartswith', 'iendswith'],
            'email': ['icontains', 'istartswith', 'iendswith'], }
        interfaces = (relay.Node,)


class Mutation(graphene.ObjectType):
    """Mutation """

    create_user = auth.CreateUser.Field()
    update_user = auth.UpdateUser.Field()
    login = auth.Login.Field()
    logout = auth.Logout.Field()


class Query(graphene.ObjectType):
    """Query"""

    viewer = gdtools.ModelField(auth.User, description='Current user.')

    def resolve_viewer(self, info: gdtools.ResolveInfo):
        user = info.context.user
        if user.is_anonymous:
            return None
        return user

    users = gdtools.ModelFilterConnectionField(auth.User)


SCHEMA = graphene.Schema(
    query=Query,
    mutation=Mutation,
    auto_camelcase=False)
