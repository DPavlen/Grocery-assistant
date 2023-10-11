from django.contrib.auth.models import AbstractUser
from django.db import models, IntegrityError
from django.db.models import F, Q
from django.db.models import CheckConstraint, UniqueConstraint

from core.constants import LenghtField
# from core.validators import validate_username
from core.validators import (
    username_validator, first_name_validator, last_name_validator)


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
        max_length=LenghtField.MAX_LENGHT_EMAIL.value,
        unique=True,
        verbose_name='email address',
    )
    username = models.CharField(
        'Логин пользователя',
        max_length=LenghtField.MAX_LENGHT_USERNAME.value,
        unique=True,
        validators=[username_validator]
    )
    first_name = models.CharField(
        'Имя пользователя',
        max_length=LenghtField.MAX_LENGHT_FIRST_NAME.value,
        validators=[first_name_validator]
    )
    last_name = models.CharField(
        'Фамилия пользователя',
        max_length=LenghtField.MAX_LENGHT_LAST_NAME.value,
        validators=[last_name_validator]
    )
    password = models.CharField(
        'Пароль пользователя',
        max_length=LenghtField.MAX_LENGHT_PASSWORD.value,
    )
    role = models.TextField(
        'Пользовательская роль юзера',
        choices=RoleChoises.choices,
        default=RoleChoises.USER,
        max_length=LenghtField.MAX_LENGHT_ROLE.value,
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
    date_sub(datetime): Дата подписки. 
    Ограничение, что уникальности логинов атора и юзера.
    Ограничение, что подписчик и автор не могут быть одинаковые. 
    """

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
            CheckConstraint(
                check=~Q(user=F('author')),
                name='not subscribe to yourself! '
            ),
            UniqueConstraint(fields=['user', 'author'],
                             name='unique_subscription'),
            
        ]

    def __str__(self):
        return f'{self.user.username} подписан на {self.author.username}'
