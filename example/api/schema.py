"""GraphQl schema.  """

import django_filters
import graphene
from django.contrib.auth.models import Group, User
from graphene import relay
from graphene_django import DjangoObjectType

import graphene_django_tools as gdtools
from graphene_django_tools import auth

from . import models


class UserFilterSet(django_filters.FilterSet):
    order_by = django_filters.OrderingFilter(
        fields=['username', 'email', 'id'])

    class Meta:
        model = User
        fields = {
            'username': ['icontains', 'istartswith', 'iendswith'],
            'email': ['icontains', 'istartswith', 'iendswith'], }


class UserNode(gdtools.ModelNode):
    class Meta:
        model = User
        interfaces = (relay.Node,)
        filterset_class = UserFilterSet


class GroupNode(DjangoObjectType):
    class Meta:
        model = Group
        filter_fields = []
        interfaces = (relay.Node,)

    this = gdtools.ModelField(Group)
    this_list = gdtools.ModelListField(Group)


class CreateGroup(gdtools.ModelCreationMutation):
    class Meta:
        model = Group
        fields = gdtools.get_all_fields
        required = ['users']


class UpdateGroup(gdtools.ModelUpdateMutation):
    class Meta:
        model = Group
        fields = gdtools.get_all_fields


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


class BulkCreateGroup(gdtools.ModelBulkCreationMutation):
    class Meta:
        model = Group
        fields = gdtools.get_all_fields
        required = ['users']


class BulkUpdateGroup(gdtools.ModelBulkUpdateMutation):
    class Meta:
        model = Group
        fields = gdtools.get_all_fields


class DeleteNode(gdtools.NodeDeleteMutation):
    class Meta:
        allowed_cls = (Group,)


class Resolver(gdtools.Resolver):
    schema = {
        "args": {
            "key": str,
            "value": str,
        },
        "type": 'Int!',
        "description": "created from `Resolver`."
    }

    def resolve(self, **kwargs):
        print({"kwargs": kwargs})
        return 42


class FooResolver(gdtools.Resolver):
    schema = int

    def resolve(self, **kwargs):
        print({"parent": self.parent})
        return self.parent['bar']


class BarResolver(gdtools.Resolver):
    schema = {
        "args": {
            "bar": int
        },
        "type": {
            "foo": FooResolver
        },
    }

    def resolve(self, **kwargs):
        return kwargs


class State(graphene.Enum):
    A = 1


class EnumResolver(gdtools.Resolver):
    schema = {
        'args': {
            'value': {
                'type': State,
                'required': True
            },
        },
        'type': State
    }

    def resolve(self, **kwargs):
        return kwargs['value']


class ModelFieldResolver(gdtools.Resolver):
    schema = {
        'args': {
            'value': models.Task._meta.get_field('state')
        },
        'type': models.Task._meta.get_field('state')
    }

    def resolve(self, **kwargs):
        return kwargs['value']


class ComplicatedResolver(gdtools.Resolver):
    _input_schema = {
        "type": {"type": str},
        "data": [
            {
                "type":
                {
                    "key": {
                        "type": str,
                        "required": True,
                        "description": "<description>",
                    },
                    "value": int,
                    "extra": {
                        "type": ['String!'],
                        "deprecation_reason": "<deprecated>"
                    },
                },
                "required": True
            },
        ],
    }
    schema = {
        "args": {
            "input": _input_schema
        },
        "type": _input_schema,
        "description": "description",
        "deprecation_reason": None
    }

    def resolve(self, **kwargs):
        return kwargs['input']


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
    mutation_resolver = Resolver.as_field()


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

    query_resolver = Resolver.as_field()
    nested_resolver = BarResolver.as_field()
    complicated_resolver = ComplicatedResolver.as_field()
    enum_resolver = EnumResolver.as_field()
    model_field_resolver = ModelFieldResolver.as_field()


SCHEMA = graphene.Schema(
    query=Query,
    mutation=Mutation,
    auto_camelcase=False)
