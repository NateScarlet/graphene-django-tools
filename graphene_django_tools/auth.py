"""Example schema for django auth.  """

import graphene
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password

import graphene_django_tools as gdtools
from graphene_django_tools.interfaces import MessageMutation

if not gdtools.get_modelnode(User, is_autocreate=False):
    gdtools.create_modelnode(
        User,
        filter_fields={
            'id': ['exact'],
            'username': ['exact', 'iexact', 'icontains', 'istartswith']})


class UserMutation(gdtools.ModelMutaion):
    """Addtional actions for user.  """

    class Meta:
        model = User

    @classmethod
    def premutate(cls, context, **arguments):
        super().premutate(context, **arguments)
        nodedata = context.data['nodedata']

        password = nodedata.get('password')
        if password:
            validate_password(password)

    @classmethod
    def postmutate(cls, context: gdtools.MutationContext,
                   result: graphene.ObjectType,
                   **arguments) -> graphene.ObjectType:

        nodedata = context.data['nodedata']
        instance = context.data['instance']

        password = nodedata.get('password')
        if password:
            instance.set_password(password)

        return super().postmutate(context, result, **arguments)


class UserCreation(UserMutation, gdtools.ModelCreationMutaion):
    """Create user.  """

    class Meta:
        model = User
        require_arguments = ('username', 'password')
        exclude_arguments = ('is_staff', 'is_superuser', 'is_active',
                             'user_permissions', 'groups', 'date_joined',
                             'last_login')


class UserUpdate(UserMutation, gdtools.ModelUpdateMutaion):
    """Update user.  """

    class Meta:
        model = User
        exclude_arguments = ('username', 'last_login')


class Login(gdtools.Mutation):
    """Login current user.  """

    class Arguments:
        username = graphene.String(required=True)
        password = graphene.String(required=True)

    class Meta:
        interfaces = (MessageMutation,)

    user = gdtools.ModelField(User)

    @classmethod
    def mutate(cls, context: gdtools.MutationContext, **kwargs):
        request = context.info.context
        user = authenticate(**kwargs)
        if not user:
            raise ValueError('Login failed.')
        login(request, user)
        return cls(user=user, message=f'Welcome back, {user}.')


class Logout(gdtools.Mutation):
    """Logout current user.  """
    class Meta:
        interfaces = (MessageMutation,)

    @classmethod
    def mutate(cls, context: gdtools.MutationContext, **kwargs):
        logout(context.info.context)
        return cls('Logout successed.')
