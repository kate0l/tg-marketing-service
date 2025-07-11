from django import forms
from django.contrib.auth.forms import (
    AuthenticationForm,
    # UserChangeForm,
    # UserCreationForm,
)

from .models import User


class UserLoginForm(AuthenticationForm):
    class Meta:
        model = User
        fields = ['usernme', 'password']
        
    username = forms.CharField(
        label='Имя пользователя',
        widget=forms.TextInput(attrs={"autofocus": True,
                                      'class': 'form-control',
                                      'placeholder': 'Имя пользователя'})
    )
    password = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput(attrs={"autocomplete": "current-password",
                                          'class': 'form-control',
                                          'placeholder': 'Пароль'})
    )