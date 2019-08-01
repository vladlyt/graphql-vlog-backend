from __future__ import annotations

import graphene
from graphene_django import DjangoObjectType

from .models import User


class UserType(DjangoObjectType):
    class Meta:
        model = User
        exclude_fields = ['password']


class CreateUser(graphene.Mutation):
    user = graphene.Field(UserType)

    class Arguments:
        email = graphene.String(required=True)
        username = graphene.String(required=True)
        password = graphene.String(required=True)
        password2 = graphene.String(required=True)

    def mutate(self,
               info: graphene.ResolveInfo,
               email: str,
               username: str,
               password: str,
               password2: str) -> CreateUser:
        if password != password2:
            raise ValueError("Passwords must be equal")

        user = User.objects.create_user(email, username, password)
        return CreateUser(user=user)


class UpdateUser(graphene.Mutation):
    user = graphene.Field(UserType)

    class Arguments:
        id = graphene.ID(required=True)
        is_staff = graphene.Boolean()
        is_admin = graphene.Boolean()
        is_active = graphene.Boolean()

    def mutate(self,
               info: graphene.ResolveInfo,
               id,
               is_staff: bool = None,
               is_admin: bool = None,
               is_active: bool = None):
        user = info.context.user
        if not user.is_authenticated:
            return UpdateUser(user=user)

        user_obj = User.objects.get(id=id)
        if (user.id == id or user.is_admin or user.is_staff) and is_active is not None:
            user_obj.is_active = is_active
        if user.is_admin and is_admin is not None:
            user_obj.is_admin = is_admin
        if user.is_staff and is_staff is not None:
            user_obj.is_staff = is_staff
        user_obj.save()
        return UpdateUser(user=user_obj)


class DeleteUser(graphene.Mutation):
    user = graphene.Field(UserType)

    class Arguments:
        id = graphene.ID(required=True)

    def mutate(self, info: graphene.ResolveInfo, id):
        user = info.context.user
        if user.is_authenticated and (user.id == id or user.is_staff):
            user = User.objects.get(id=id)
            user.delete()
        return DeleteUser(user=user)


class UserQuery(graphene.ObjectType):
    user = graphene.Field(UserType, id=graphene.ID())
    all_users = graphene.List(UserType)

    def resolve_user(self, info: graphene.ResolveInfo, id):
        return User.objects.get(id=id) if id else None

    def resolve_all_users(self, info: graphene.ResolveInfo, **kwargs):
        print(kwargs)
        return User.objects.all()


class UserMutation(graphene.ObjectType):
    create_user = CreateUser.Field()
    update_user = UpdateUser.Field()
    delete_user = DeleteUser.Field()
