from django.contrib.auth.models import AbstractUser
from django.db import models


# Create your models here.
class User(AbstractUser):
    avatar_image = models.CharField(verbose_name='url изображения профиля', blank=True, null=True)
    role = models.CharField(verbose_name='роль',
                            max_length=150)
    bio = models.CharField(max_length=200, verbose_name='о себе', blank=True)
    email = models.EmailField(verbose_name="email адрес", blank=True, unique=True)

    ROLE_CHOICES = [
        ('guest', 'Гость'),
        ('user', 'Пользователь'),
    ]
    role = models.CharField(
        verbose_name='Роль',
        max_length=20,
        choices=ROLE_CHOICES,
        default='guest'
    )

    class Meta:
        db_table = 'users'
        verbose_name = 'Пользователя'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.get_full_name()

    @property
    def is_partner(self):
        return hasattr(self, 'partner_profile') and self.partner_profile.status == 'active'


class PartnerProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='partner_profile'
    )
    status = models.CharField(
        verbose_name='Статус',
        max_length=20,
        choices=[
            ('active', 'Активен'),
            ('pending', 'На рассмотрении'),
            ('rejected', 'Отклонён'),
            ('suspended', 'Приостановлен')
        ],
        default='pending'
    )
    partner_since = models.DateTimeField(
        verbose_name='Партнёр с',
        auto_now_add=True
    )
    balance = models.DecimalField(
        verbose_name='Баланс',
        max_digits=10,
        decimal_places=2,
        default=0
    )
    payment_details = models.TextField(
        verbose_name='Платёжные реквизиты',
        blank=True
    )

    class Meta:
        verbose_name = 'Профиль партнёра'
        verbose_name_plural = 'Профили партнёров'

    def __str__(self):
        return f"Профиль партнёра: {self.user.username}"