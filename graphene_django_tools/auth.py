"""Example schema for django auth.  """

import graphene
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password

import graphene_django_tools as gdtools


class UserMutation(gdtools.ModelMutaion):
    """Addtional actions for user.  """

    class Meta:
        model = User

    @classmethod
    def premutate(cls, context: gdtools.ModelMutaionContext):

        super().premutate(context)
        password = context.arguments.get('password')
        if password:
            validate_password(password)

    @classmethod
    def postmutate(cls,
                   context: gdtools.ModelMutaionContext,
                   payload: graphene.ObjectType) -> graphene.ObjectType:

        password = context.arguments.get('password')
        if password:
            context.instance.set_password(password)
        return super().postmutate(context, payload)


class CreateUser(UserMutation, gdtools.ModelCreationMutaion):
    """Create user.  """

    class Meta:
        model = User
        require = ('username', 'password')
        exclude = ('is_staff', 'is_superuser', 'is_active',
                   'user_permissions', 'groups', 'date_joined',
                   'last_login')


class UpdateUser(UserMutation, gdtools.ModelUpdateMutaion):
    """Update user.  """

    class Meta:
        model = User
        exclude = ('username', 'last_login')


class Login(gdtools.NodeMutation):
    """Login current user.  """

    class Arguments:
        username = graphene.String(required=True)
        password = graphene.String(required=True)

    class Meta:
        interfaces = (gdtools.interfaces.Message,)

    user = gdtools.ModelField(User)

    @classmethod
    def mutate(cls, context: gdtools.ModelMutaionContext):
        request = context.info.context
        user = authenticate(**context.arguments)
        if not user:
            raise ValueError('Login failed.')
        login(request, user)
        return cls(user=user, message=f'Welcome back, {user}.')


class Logout(gdtools.NodeMutation):
    """Logout current user.  """

    @classmethod
    def mutate(cls, context: gdtools.ModelMutaionContext):
        logout(context.info.context)
        return cls()


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
