from __future__ import annotations

import graphene

from .models import User
from .mutations import (
    RegisterUser,
    UpdateUser,
    DeleteUser,
)
from .types import UserType


class UserQuery(graphene.ObjectType):
    user = graphene.Field(
        UserType,
        id=graphene.Argument(graphene.ID, required=True)
    )
    current_user = graphene.Field(UserType)
    all_users = graphene.List(UserType)

    def resolve_user(self, info: graphene.ResolveInfo, id: graphene.ID):
        return User.objects.get(id=id) if id else None

    def resolve_all_users(self, info: graphene.ResolveInfo, **kwargs):
        return User.objects.all()

    def resolve_current_user(self, info: graphene.ResolveInfo):
        user = info.context.user
        return user if user.is_authenticated else None


class UserMutation(graphene.ObjectType):
    register_user = RegisterUser.Field()
    update_user = UpdateUser.Field()
    delete_user = DeleteUser.Field()
