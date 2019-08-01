from __future__ import annotations

import graphene
from django.db.models import Q

from core.mutations import BaseMutation
from core.utils import get_fields_from_input
from .models import User
from .types import UserType


# TODO add descriptions and type hints


class BaseInput(graphene.InputObjectType):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, required=True, **kwargs)


class UserRegisterInput(BaseInput):
    email = graphene.String(description="User email", required=True)
    username = graphene.String(description="User unique username", required=True)
    password = graphene.String(description="User password", required=True)
    is_active = graphene.Boolean(description="User is active")


class RegisterUser(BaseMutation):
    user = graphene.Field(UserType)

    class Arguments:
        input = UserRegisterInput(description="Fields required to register user")

    class Meta:
        description = "This mutation register user"

    @classmethod
    def mutate(cls, root, info: graphene.ResolveInfo, input: dict) -> RegisterUser:
        email, username, password, is_active = get_fields_from_input(input,
                                                                     'email', 'username',
                                                                     'password', 'is_active')
        if User.objects.filter(Q(email=email) | Q(username=username)).exists():
            return RegisterUser(errors=[cls.create_error(None, "Username and email must be unique")])
        user = User.objects.create_user(email, username, password)
        return RegisterUser(user=user)


class UpdateUser(graphene.Mutation):
    user = graphene.Field(UserType)

    class Arguments:
        id = graphene.ID(required=True)
        is_staff = graphene.Boolean()
        is_admin = graphene.Boolean()
        is_active = graphene.Boolean()

    def mutate(self,
               info: graphene.ResolveInfo,
               id: graphene.ID,
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

    def mutate(self,
               info: graphene.ResolveInfo,
               id: graphene.ID):
        user = info.context.user
        if user.is_authenticated and (user.id == id or user.is_staff):
            user = User.objects.get(id=id)
            user.delete()
        return DeleteUser(user=user)
