from django.contrib.auth.models import AbstractUser
from django.db import models

ROLE_MAXLENGTH = 150
BIO_MAXLENGTH = 200

# Create your models here.
class User(AbstractUser):
    avatar_image = models.CharField(verbose_name='url изображения профиля', blank=True, null=True)
    role = models.CharField(verbose_name='роль',
                            max_length=ROLE_MAXLENGTH)
    bio = models.CharField(max_length=BIO_MAXLENGTH, verbose_name='о себе', blank=True)
    email = models.EmailField(verbose_name="email адрес", blank=True, unique=True)
    class Meta:
        db_table = 'users'
        verbose_name = 'Пользователя'
        verbose_name_plural = 'Пользователи'
    
    def __str__(self):
        return self.get_full_name()