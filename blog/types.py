from graphene import relay
from graphene_django import DjangoObjectType

from .models import Post


class PostType(DjangoObjectType):
    class Meta:
        description = 'Represents a post'
        model = Post
        interfaces = [relay.Node]
