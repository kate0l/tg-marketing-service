from django import forms

from config.users.models import User
# from config.channel.models import Channel
from .models import Group


class TaskForm(forms.ModelForm):
    name = forms.CharField(
        max_length=150,
        required=True,
        label='Название группы',
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'autofocus': True,
            }
        )
    )
    description = forms.CharField(
        required=False,
        label='Описание',
        widget=forms.Textarea(
            attrs={
                'class': 'form-control',
                'rows': 3,
            }
        )
    )
    image_url = forms.CharField(
        required=False,
        label='Изображение (URL)',
        widget=forms.URLInput(
            attrs={
                'placeholder':'https://example.com/image.jpg',
                'class': 'form-control'
            }
        )
    )
    
    class Meta:
        model = Group
        fields = ('name', 'description', 'image_url',)