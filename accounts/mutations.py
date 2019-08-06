import graphene

from core.mutations import ModelMutation, ModelDeleteMutation, BaseInput
from .models import User


class UserInput(BaseInput):
    email = graphene.String(description="User email")
    username = graphene.String(description="User unique username")
    is_active = graphene.Boolean(description="User is active")


class UserRegisterInput(UserInput):
    password = graphene.String(description="User password", required=True)


class RegisterUser(ModelMutation):
    class Arguments:
        input = UserRegisterInput(description="Fields required to register user")

    class Meta:
        description = 'Register a new user'
        exclude = ['password']
        model = User

    @classmethod
    def save(cls, info, user: User, cleaned_input: dict):
        password = cleaned_input['password']
        user.set_password(password)
        user.save()


class UpdateUser(ModelMutation):
    class Arguments:
        id = graphene.ID(description='User id for update', required=True)
        input = UserInput(description="Fields required to update user")

    class Meta:
        description = 'This mutation updates user'
        exclude = ['password']
        model = User


class DeleteUser(ModelDeleteMutation):
    class Arguments:
        id = graphene.ID('User delete id', required=True)

    class Meta:
        description = 'This mutation deletes user'
        model = User

    @classmethod
    def user_is_allowed(cls, user: User, input: dict = None, id: graphene.ID = None):
        return user.is_authenticated and (user.is_staff or user.id == id)
