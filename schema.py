import graphene

from accounts.schema import UserQuery, UserMutation
from blog.schema import PostQuery, PostMutation


# TODO crete BaseQuery and BaseMutation for queries and mutations
# TODO add author/user to post
# TODO rebuild all queries and mutations to higher level with Node

class Query(PostQuery, UserQuery):
    ...


class Mutation(PostMutation, UserMutation):
    ...


schema = graphene.Schema(Query, Mutation)
