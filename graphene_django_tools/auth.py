"""Example schema for django auth.  """

import graphene
from django.contrib.auth import authenticate, get_user_model, login, logout
from django.contrib.auth.password_validation import validate_password

import graphene_django_tools as gdtools

User = get_user_model()  # pylint: disable=invalid-name


class UserMutation(gdtools.ModelMutation):
    """Additional actions for user.  """

    class Meta:
        abstract = True

    @classmethod
    def premutate(cls, context: gdtools.ModelMutationContext):

        super().premutate(context)
        password = context.mapping.get('password')
        if password:
            validate_password(password)

    @classmethod
    def postmutate(cls,
                   context: gdtools.ModelMutationContext,
                   payload: graphene.ObjectType) -> graphene.ObjectType:

        password = context.mapping.get('password')
        if password:
            context.instance.set_password(password)
        context.instance.full_clean()
        return super().postmutate(context, payload)


class CreateUser(UserMutation, gdtools.ModelCreationMutation):
    """Create user.  """

    class Meta:
        model = User
        fields = ('username', 'password', 'first_name', 'last_name', 'email')
        require = ('username', 'password')


class UpdateUser(UserMutation, gdtools.ModelUpdateMutation):
    """Update user.  """

    class Meta:
        model = User
        fields = ('username', 'password', 'first_name', 'last_name', 'email')


class Login(gdtools.NodeMutation):
    """Login current user.  """

    class Arguments:
        username = graphene.String(required=True)
        password = graphene.String(required=True)

    user = gdtools.ModelField(User)

    @classmethod
    def mutate(cls, context: gdtools.ModelMutationContext):
        request = context.info.context
        user = authenticate(request, **context.arguments)
        if not user:
            raise ValueError('Login failed.')
        login(request, user)
        return cls(user=user)


class Logout(gdtools.NodeMutation):
    """Logout current user.  """

    @classmethod
    def mutate(cls, context: gdtools.ModelMutationContext):
        logout(context.info.context)
        return cls()
