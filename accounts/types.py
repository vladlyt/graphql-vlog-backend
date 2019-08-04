from graphene import relay
from graphene_django import DjangoObjectType

from .models import User


class UserType(DjangoObjectType):
    class Meta:
        description = 'Represents a user'
        model = User
        exclude_fields = ['password']
        interfaces = [relay.Node]
