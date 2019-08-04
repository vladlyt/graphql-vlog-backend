import graphene

from .models import Post
from .mutations import CreatePost, UpdatePost, DeletePost
from .types import PostType


class PostQuery(graphene.ObjectType):
    post = graphene.Field(PostType, id=graphene.ID())
    all_posts = graphene.List(PostType)

    def resolve_post(self, info: graphene.ResolveInfo, id):
        return Post.objects.get(id=id) if id else None

    def resolve_all_posts(self, info: graphene.ResolveInfo, **kwargs):
        return Post.objects.all()


class PostMutation(graphene.ObjectType):
    create_post = CreatePost.Field()
    update_post = UpdatePost.Field()
    delete_post = DeletePost.Field()
