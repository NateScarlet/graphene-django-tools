from django.contrib.auth.models import User
from graphene.relay.node import Node


class UserNode(Node):
    class Meta:
        model = User
        filter_fields = {
            'id': ['exact'],
            'username': ['exact', 'iexact', 'icontains', 'istartswith']}
