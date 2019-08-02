import graphene

from core.mutations import BaseMutation, BaseInput
from core.utils import get_fields_from_input
from .models import User
from .types import UserType


class UserInput(BaseInput):
    email = graphene.String(description="User email")
    username = graphene.String(description="User unique username")
    is_active = graphene.Boolean(description="User is active")


class UserRegisterInput(UserInput):
    password = graphene.String(description="User password", required=True)


class RegisterUser(BaseMutation):
    user = graphene.Field(UserType)

    class Arguments:
        input = UserRegisterInput(description="Fields required to register user")

    class Meta:
        description = "This mutation register user"

    @classmethod
    def mutate(cls, root,
               info: graphene.ResolveInfo,
               input: dict):
        errors, fields = [], ['email', 'username', 'password', 'is_active']
        email, username, password, is_active = get_fields_from_input(input, fields)
        if email is None:
            errors.append(cls.create_error('email', "RegisterUser must contain email"))
        if username is None:
            errors.append(cls.create_error('username', "Register user must contain username"))
        if email is not None and User.objects.filter(email=email).exists():
            errors.append(cls.create_error('email', "This email is already exists"))
        if username is not None and User.objects.filter(username=username).exists():
            errors.append(cls.create_error('username', "This username is already exists"))

        if errors:
            return RegisterUser(errors=errors)
        user = User.objects.create_user(email, username, password)
        return RegisterUser(user=user)


class UpdateUser(BaseMutation):
    user = graphene.Field(UserType)

    class Arguments:
        id = graphene.ID(description='User id for update', required=True)
        input = UserInput(description="Fields required to update user")

    class Meta:
        description = 'This mutation updates user'

    @classmethod
    def mutate(cls, root,
               info: graphene.ResolveInfo,
               id: graphene.ID,
               input: dict):
        user, errors = info.context.user, []

        if not user.is_authenticated:
            errors.append(cls.create_error('user', 'User must be authenticated'))

        if user.is_staff or user.is_admin or user.id == id:
            user_obj = User.objects.get(id=id)
            fields = ['email', 'username', 'is_active']
            email, username, is_active = get_fields_from_input(input, fields)
            if email is not None and not User.objects.filter(email=email).exists():
                user_obj.email = email
            else:
                errors.append(cls.create_error('email', 'This email is already exists'))
            if username is not None and not User.objects.filter(username=username).exists():
                user_obj.username = username
            else:
                errors.append(cls.create_error('username', 'This username is already exists'))
            if is_active is not None:
                user_obj.is_active = user_obj

            if not errors:
                user_obj.save()
                return UpdateUser(user=user_obj)
            else:
                return UpdateUser(errors=errors)
        return UpdateUser(errors=[cls.create_error('None', 'User must be authenticated, admin or staff')])


class DeleteUser(BaseMutation):
    user = graphene.Field(UserType)

    class Arguments:
        id = graphene.ID('User delete id', required=True)

    class Meta:
        description = 'This mutation deletes user'

    @classmethod
    def mutate(cls, root,
               info: graphene.ResolveInfo,
               id: graphene.ID):
        user = info.context.user
        if user.is_authenticated and (user.id == id or user.is_staff):
            user = User.objects.get(id=id)
            user.delete()
            return DeleteUser(user=user)
        return DeleteUser(errors=[cls.create_error(None, 'User must be deleted user or staff')])
