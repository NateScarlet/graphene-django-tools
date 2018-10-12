"""Example schema for django auth.  """

import graphene
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password

import graphene_django_tools as gdtools

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
    def premutate(cls, context: gdtools.ModelMutaionContext):

        super().premutate(context)
        password = context.arguments.get('password')
        if password:
            validate_password(password)

    @classmethod
    def postmutate(cls,
                   context: gdtools.ModelMutaionContext,
                   response: graphene.ObjectType) -> graphene.ObjectType:

        password = context.arguments.get('password')
        if password:
            context.instance.set_password(password)
        return super().postmutate(context, response)


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


class Login(gdtools.ClientIDMutation):
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


class Logout(gdtools.ClientIDMutation):
    """Logout current user.  """

    @classmethod
    def mutate(cls, context: gdtools.ModelMutaionContext):
        logout(context.info.context)
        return cls()
