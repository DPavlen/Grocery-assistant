from django.contrib.auth.models import AbstractBaseUser, UserManager
from django.db import models


class User(AbstractBaseUser):
    """Кастомная модель переопределенного юзера.
    При создании пользователя все поля обязательны для заполнения."""
    class RoleChoice(models.TextChoices):
        """Определение роли юзера."""
        USER = "user"
        MODERATOR = "moderator"
        ADMIN = "admin"

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    username = models.CharField(
        "Имя пользователя",
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
        unique=True
    )
    last_name = models.CharField(
        "Фамилия пользователя",
        max_length=254,
        unique=True
    )
    role = models.TextField(
        "Пользовательская роль юзера",
        choices=RoleChoice.choices,
        #default=RoleChoice.USER,
        max_length=50
    )
    # UserManager класс или компонент, отвечающий за управление пользователями в системе.
    objects = UserManager()

    @property
    def is_admin(self):
        return self.role == User.RoleChoises.ADMIN or self.is_superuser

    @property
    def is_moderator(self):
        return self.role == User.RoleChoises.MODERATOR or self.is_moderator

    @property
    def is_user(self):
        return self.role == User.RoleChoises.USER

    class Meta:
        ordering = ("id",)
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return f"{self.username}: {self.email}"


#Обязательные поля для пользователя:
#логин,
#пароль,
#email,
#имя,
#фамилия.