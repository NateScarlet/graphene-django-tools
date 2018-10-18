"""GrapQl schema.  """

import graphene
from django.contrib.auth.models import User
from graphene import relay
from graphene_django import DjangoObjectType

import graphene_django_tools as gdtools
from graphene_django_tools import auth

from .models import Group


class UserNode(DjangoObjectType):
    class Meta:
        model = User
        filter_fields = {
            'username': ['icontains', 'istartswith', 'iendswith'],
            'email': ['icontains', 'istartswith', 'iendswith'], }
        interfaces = (relay.Node,)


class GroupNode(DjangoObjectType):
    class Meta:
        model = Group
        filter_fields = []
        interfaces = (relay.Node,)


class CreateGroup(gdtools.ModelCreationMutaion):
    class Meta:
        model = Group
        required = ['users']


class UpdateGroup(gdtools.ModelUpdateMutaion):
    class Meta:
        model = Group


class Mutation(graphene.ObjectType):
    """Mutation """

    create_user = auth.CreateUser.Field()
    update_user = auth.UpdateUser.Field()
    login = auth.Login.Field()
    logout = auth.Logout.Field()
    node_echo = auth.NodeEcho.Field()
    create_group = CreateGroup.Field()
    update_group = UpdateGroup.Field()


class Query(graphene.ObjectType):
    """Query"""

    viewer = gdtools.ModelField(auth.User, description='Current user.')

    def resolve_viewer(self, info: gdtools.ResolveInfo):
        user = info.context.user
        if user.is_anonymous:
            return None
        return user

    users = gdtools.ModelFilterConnectionField(auth.User)
    groups = gdtools.ModelFilterConnectionField(Group)

    def resolve_groups(self, info: gdtools.ResolveInfo):
        print(info)


SCHEMA = graphene.Schema(
    query=Query,
    mutation=Mutation,
    auto_camelcase=False)
