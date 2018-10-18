from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()  # pylint:disable=invalid-name
# Create your models here.


class Group(models.Model):
    name = models.CharField('Group name', max_length=30)
    users = models.ManyToManyField(
        User, verbose_name='A group contains many user.')
