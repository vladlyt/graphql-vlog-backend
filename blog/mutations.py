import graphene

from accounts.models import User
from core.mutations import BaseInput, ModelMutation, ModelDeleteMutation
from .models import Post, PostStatusEnum


class PostInput(BaseInput):
    title = graphene.String(description='Post title')
    body = graphene.String(description='Post body')
    publish_date = graphene.DateTime(description='DateTime when Post will be published')
    status = graphene.Argument(graphene.Enum.from_enum(
        PostStatusEnum,
        description=lambda v: f'{v} status',
    ))


class PostCreateInput(PostInput):
    author_id = graphene.ID(description='Author id for post', required=True)


class CreatePost(ModelMutation):
    class Arguments:
        input = PostCreateInput(description='Input for create post')

    class Meta:
        model = Post
        description = 'Mutation for create post'

    @classmethod
    def user_is_allowed(cls, user: User, input: dict = None):
        return user.is_authenticated and (user.is_admin or user.id == input.get('id'))


class UpdatePost(ModelMutation):
    class Arguments:
        id = graphene.ID(required=True)
        input = PostInput(description='Input for update post')

    class Meta:
        model = Post
        description = 'Mutation for update post'


class DeletePost(ModelDeleteMutation):
    class Arguments:
        id = graphene.ID(description='Post id for delete', required=True)

    class Meta:
        model = Post
        description = 'Mutation for delete post'

    @classmethod
    def user_is_allowed(cls, user: User, input: dict = None):
        # TODO implement here get_database_id for id from input
        return user.is_authenticated and (user.is_admin or user.id == id)
