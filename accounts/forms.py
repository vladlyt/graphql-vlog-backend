from django.contrib.auth import forms
from django.contrib.auth import get_user_model

User = get_user_model()


class UserCreationForm(forms.UserCreationForm):
    class Meta(forms.UserCreationForm):
        model = User
        fields = ('email',
                  'username',
                  'password',
                  'is_active',
                  'is_admin',
                  'is_staff')


class UserChangeForm(forms.UserChangeForm):
    class Meta:
        model = User
        fields = forms.UserChangeForm.Meta.fields
