"""Predefined mutation for django auth.  """

import graphene
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password

from .mutation import (ModelCreationMutaion, ModelMutaion, ModelUpdateMutaion,
                       MutationContext)


class UserMutation(ModelMutaion):
    """Addtional actions for user.  """

    class Meta:
        model = User

    @classmethod
    def premutate(cls, context, **arguments):
        super().premutate(context, **arguments)
        nodedata = context.data['nodedata']
        validate_password(nodedata['password'])

    @classmethod
    def postmutate(cls, result: graphene.ObjectType,
                   context: MutationContext,
                   **arguments) -> graphene.ObjectType:

        nodedata = context.data['nodedata']
        instance = context.data['instance']

        password = nodedata.get('password')
        if password:
            instance.set_password(password)

        return super().postmutate(result, context, **arguments)


class UserCreation(UserMutation, ModelCreationMutaion):
    """Create user.  """

    class Meta:
        model = User
        require_arguments = ('username', 'password')
        exclude_arguments = ('is_staff', 'is_superuser', 'is_active',
                             'user_permissions', 'groups', 'date_joined',
                             'last_login')


class UserUpdate(UserMutation, ModelUpdateMutaion):
    """Update user.  """

    class Meta:
        model = User
        exclude_arguments = ('username', 'last_login')
