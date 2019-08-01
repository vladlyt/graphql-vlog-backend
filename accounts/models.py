from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models


class UserManager(BaseUserManager):
    def create_user(self, email, username, password, is_active=True, is_staff=False, is_admin=False):
        if not email:
            raise ValueError("User must contain an email")
        if not password:
            raise ValueError("User must contain an password")
        user = self.model(
            email=self.normalize_email(email),
            username=username,
            is_admin=is_admin,
            is_staff=is_staff,
            is_active=is_active,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_staffuser(self, email, username, password):
        user = self.create_user(
            email,
            username,
            password,
            is_staff=True
        )
        return user

    def create_superuser(self, email, username, password):
        user = self.create_user(
            email,
            username,
            password,
            is_staff=True,
            is_admin=True
        )
        return user


class User(AbstractBaseUser):
    email = models.EmailField(max_length=255, unique=True)
    username = models.CharField(max_length=255, default="noname")
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'

    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.get_full_name()

    def get_full_name(self):
        return self.username or self.email

    def get_short_name(self):
        return self.username or self.email

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True
