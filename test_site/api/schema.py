"""GrapQl schema.  """

import graphene
from django.contrib.auth.models import Group, User
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


class GroupNode(DjangoObjectType):
    class Meta:
        model = Group
        filter_fields = []
        interfaces = (relay.Node,)

    this = gdtools.ModelField(Group)
    this_list = gdtools.ModelListField(Group)


class CreateGroup(gdtools.ModelCreationMutaion):
    class Meta:
        model = Group
        required = ['users']


class UpdateGroup(gdtools.ModelUpdateMutaion):
    class Meta:
        model = Group


class IDInInput(graphene.InputObjectType):
    node_id = graphene.ID()
    node_id_list = graphene.List(graphene.ID)


class NodeEcho(gdtools.NodeUpdateMutation):
    """Example non-model mutation.  """

    class Arguments:
        extra_nodes = graphene.List(graphene.ID)
        input = IDInInput().Field()

    message = graphene.String(required=True)
    extra_nodes = graphene.List(graphene.Node)
    input_node = graphene.Field(graphene.Node)
    input_nodes = graphene.List(graphene.Node)

    @classmethod
    def mutate(cls, context: gdtools.NodeUpdateMutation):
        input_ = context.arguments.get('input', {})
        return cls(message=repr(context.node),
                   extra_nodes=context.arguments.get('extra_nodes'),
                   input_node=input_.get('node_id'),
                   input_nodes=input_.get('node_id_list'))


class BulkCreateGroup(gdtools.ModelBulkCreationMutaion):
    class Meta:
        model = Group
        required = ['users']


class BulkUpdateGroup(gdtools.ModelBulkUpdateMutaion):
    class Meta:
        model = Group


class DeleteNode(gdtools.NodeDeleteMutation):
    class Meta:
        allowed_cls = (Group,)


class Mutation(graphene.ObjectType):
    """Mutation """

    create_user = auth.CreateUser.Field()
    update_user = auth.UpdateUser.Field()
    login = auth.Login.Field()
    logout = auth.Logout.Field()
    node_echo = NodeEcho.Field()
    delete_node = DeleteNode.Field()
    create_group = CreateGroup.Field()
    update_group = UpdateGroup.Field()
    bulk_create_group = BulkCreateGroup.Field()
    bulk_update_group = BulkUpdateGroup.Field()


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

    recursive_group = gdtools.ModelField(Group)

    def resolve_recursive_group(self, info: gdtools.ResolveInfo):
        ret = Group.objects.first()
        ret.this = ret
        ret.this_list = [ret]
        return ret


SCHEMA = graphene.Schema(
    query=Query,
    mutation=Mutation,
    auto_camelcase=False)
