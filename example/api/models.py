from django.db import models


class Task(models.Model):

    state = models.CharField('state',
                             max_length=2,
                             choices=(
                                 ('A', 'A state'),
                                 ('B', 'B state'),
                             ))
