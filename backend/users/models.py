from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import UniqueConstraint

from core.constants import Lenght
# from core.validators import validate_username
from core.validators import (UsernameValidator, FirstNameValidator,
                            LastNameValidator)




class User(AbstractUser):
    """Кастомная модель переопределенного юзера.
    При создании пользователя все поля обязательны для заполнения."""
    class RoleChoises(models.TextChoices):
        """Определение роли юзера."""
        USER = 'user'
        MODERATOR = 'moderator'
        ADMIN = 'admin'

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = [
        'username',
        'first_name',
        'last_name',
    ]
    email = models.EmailField(
        max_length=Lenght.MAX_LENGHT_EMAIL.value,
        unique=True,
        verbose_name='email address',
    )
    username = models.CharField(
        'Логин пользователя',
        max_length=Lenght.MAX_LENGHT_USERNAME.value,
        unique=True,
        validators=[UsernameValidator()]
    )
    first_name = models.CharField(
        'Имя пользователя',
        max_length=Lenght.MAX_LENGHT_FIRST_NAME.value,
        validators=[FirstNameValidator()]
    )
    last_name = models.CharField(
        'Фамилия пользователя',
        max_length=Lenght.MAX_LENGHT_LAST_NAME.value,
        validators=[LastNameValidator()]
    )
    password = models.CharField(
        'Пароль пользователя',
        max_length=Lenght.MAX_LENGHT_PASSWORD.value,
    )
    role = models.TextField(
        'Пользовательская роль юзера',
        choices=RoleChoises.choices,
        default=RoleChoises.USER,
        max_length=Lenght.MAX_LENGHT_ROLE.value,
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ['-id']

    def __str__(self):
        return str(self.username)


class Subscriptions(models.Model):
    """Подписки пользователей на друг друга.
    author(int): Автор рецепта. Связь через ForeignKey.
    user(int): Подписчик. Cвязь через ForeignKey.
    date_sub(datetime): Дата подписки."""

    author = models.ForeignKey(
        User,
        verbose_name='Автор рецепта',
        related_name='subscribe',
        on_delete=models.CASCADE,
    )
    user = models.ForeignKey(
        User,
        verbose_name='Подписчик',
        related_name='subscription',
        on_delete=models.CASCADE,
    )
    date_sub = models.DateTimeField(
        verbose_name='Дата создания подписки',
        auto_now_add=True,
        editable=False,
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        ordering = ('-id',)
        constraints = [
            UniqueConstraint(fields=['user', 'author'],
                             name='unique_subscription')
        ]

    def __str__(self):
        return f'{self.user.username} подписан на {self.author.username}'
