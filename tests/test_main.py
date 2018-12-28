import django
import graphene
import pytest
from django.contrib.auth.forms import UserChangeForm
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password

import graphene_django_tools


class UserCreationMutation(graphene_django_tools.DjangoModelCreationMutation):
    class Meta:
        model = User

    @classmethod
    def validate_input(cls, value, field: django.db.models.Field):
        if field.name == 'password':
            validate_password(value)

    @classmethod
    def validate_field(cls, field: django.db.models.Field):
        if field.name not in ['username', 'password']:
            raise KeyError('Not allowed', field.name)

    @classmethod
    def process_output(cls, value, field: django.db.models.Field):
        ret = value
        if field.name == 'password':
            ret = make_password(value)
        return ret


class UserUpdateMutation(graphene_django_tools.DjangoModelCreationMutation):
    class Meta:
        model = User

    @classmethod
    def validate_field(cls, field: django.db.models.Field):
        if field.name not in ['username', 'password']:
            raise KeyError('Not allowed', field.name)

    @classmethod
    def process_output(cls, value, field: django.db.models.Field):
        ret = value
        if field.name == 'password':
            ret = make_password(value)
        return ret


class Mutation(graphene.Mutation):
    creation = UserCreationMutation.Field()
    update = UserUpdateMutation.Field()


SCHEMA = graphene.Schema(mutation=Mutation)


@pytest.fixture(name='client')
def _client():
    return graphene.test.Client(SCHEMA)
