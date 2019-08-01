import graphene
from graphene_django import DjangoObjectType

from .models import Post


class PostType(DjangoObjectType):
    class Meta:
        model = Post


class CreatePost(graphene.Mutation):
    post = graphene.Field(PostType)

    class Arguments:
        title = graphene.String(required=True)
        body = graphene.String(required=True)

    def mutate(self, info: graphene.ResolveInfo, title, body):
        post = Post.objects.create(
            author=info.context.user,
            title=title,
            body=body,
        )
        post.save()
        return CreatePost(post=post)


class UpdatePost(graphene.Mutation):
    post = graphene.Field(PostType)

    class Arguments:
        id = graphene.ID(required=True)
        title = graphene.String()
        body = graphene.String()
        status = graphene.Int()

    def mutate(self, info, id, title=None, body=None, status=None):
        post = Post.objects.get(id=id)
        if title is not None:
            post.title = title
        if body is not None:
            post.body = body
        if status is not None:
            post.status = status
        post.save()
        return UpdatePost(post=post)


class DeletePost(graphene.Mutation):
    post = graphene.Field(PostType)

    class Arguments:
        id = graphene.ID(required=True)

    def mutate(self, info, id):
        post = Post.objects.get(id=id)
        post.delete()
        return DeletePost(post=post)


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
