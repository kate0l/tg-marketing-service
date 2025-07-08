from django.db import models
from django.contrib.auth.models import AbstractUser


# Create your models here.
class User(AbstractUser):
    avatar_image = models.URLField(verbose_name='url_изображения_профиля')
    role = models.CharField(verbose_name='роль',
                            max_length=150)
    class Meta:
        db_table = 'users'
        verbose_name = 'Пользователя'
        verbose_name_plural = 'Пользователи'
    
    def __str__(self):
        return self.get_full_name()