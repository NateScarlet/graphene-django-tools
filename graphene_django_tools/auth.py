"""Example schema for django auth.  """

import graphene
from django.contrib.auth import authenticate, get_user_model, login, logout
from django.contrib.auth.password_validation import validate_password

import graphene_django_tools as gdtools

User = get_user_model()  # pylint: disable=invalid-name


class UserMutation(gdtools.ModelMutaion):
    """Addtional actions for user.  """

    class Meta:
        abstract = True

    @classmethod
    def premutate(cls, context: gdtools.ModelMutaionContext):

        super().premutate(context)
        password = context.mapping.get('password')
        if password:
            validate_password(password)

    @classmethod
    def postmutate(cls,
                   context: gdtools.ModelMutaionContext,
                   payload: graphene.ObjectType) -> graphene.ObjectType:

        password = context.mapping.get('password')
        if password:
            context.instance.set_password(password)
        context.instance.full_clean()
        return super().postmutate(context, payload)


class CreateUser(UserMutation, gdtools.ModelCreationMutaion):
    """Create user.  """

    class Meta:
        model = User
        fields = ('username', 'password', 'first_name', 'last_name', 'email')
        require = ('username', 'password')


class UpdateUser(UserMutation, gdtools.ModelUpdateMutaion):
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
    def mutate(cls, context: gdtools.ModelMutaionContext):
        request = context.info.context
        user = authenticate(**context.arguments)
        if not user:
            raise ValueError('Login failed.')
        login(request, user)
        return cls(user=user)


class Logout(gdtools.NodeMutation):
    """Logout current user.  """

    @classmethod
    def mutate(cls, context: gdtools.ModelMutaionContext):
        logout(context.info.context)
        return cls()
