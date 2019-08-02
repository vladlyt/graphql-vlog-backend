import graphene
import graphql_jwt

from accounts.schema import UserQuery, UserMutation
from blog.schema import PostQuery, PostMutation


class Query(PostQuery, UserQuery):
    ...


class Mutation(PostMutation, UserMutation):
    token_auth = graphql_jwt.ObtainJSONWebToken.Field()
    verify_token = graphql_jwt.Verify.Field()
    refresh_token = graphql_jwt.Refresh.Field()


schema = graphene.Schema(Query, Mutation)
