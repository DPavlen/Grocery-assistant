from django.contrib.auth.models import AbstractUser
from django.db import models

# from users.validators import UsernameValidatorRegex, username_me


class User(AbstractUser):
    """Кастомная модель переопределенного юзера.
    При создании пользователя все поля обязательны для заполнения."""
    class RoleChoises(models.TextChoices):
        """Определение роли юзера."""
        USER = "user"
        MODERATOR = "moderator"
        ADMIN = "admin"

    username = models.CharField(
        "Логин пользователя",
        max_length=150,
        unique=True,
    )
    password = models.CharField(
        "Пароль пользователя",
        max_length=128,
    )
    email = models.EmailField(
        "Электронная почта",
        max_length=254,
        unique=True,
    )
    first_name = models.CharField(
        "Имя пользователя",
        max_length=254,
        blank=True
    )
    last_name = models.CharField(
        "Фамилия пользователя",
        max_length=254,
        blank=True
    )
    email = models.EmailField(
        blank=True,
        max_length=254,
        unique=True,
        verbose_name="email address",
    )
    role = models.TextField(
        "Пользовательская роль юзера",
        choices=RoleChoises.choices,
        default=RoleChoises.USER,
        max_length=50
    )

    REQUIRED_FIELDS = ["email"]
    USERNAME_FIELDS = "email"

    @property
    def is_admin(self):
        return self.role == User.RoleChoises.ADMIN or self.is_superuser

    @property
    def is_moderator(self):
        return self.role == User.RoleChoises.MODERATOR

    @property
    def is_user(self):
        return self.role == User.RoleChoises.USER

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        ordering = ["-id"]

    def __str__(self):
        return str(self.username)


#Обязательные поля для пользователя:
#логин,
#пароль,
#email,
#имя,
#фамилия.