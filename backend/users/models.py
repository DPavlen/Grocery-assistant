from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import UniqueConstraint

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

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        ordering = ["-id"]

    def __str__(self):
        return str(self.username)


class Subscription(models.Model):
    """Подписки пользователей на друг друга.
    author(int): Автор рецепта. Связь через ForeignKey.
    user(int): Подписчик. Cвязь через ForeignKey.
    date_sub(datetime): Дата подписки.
    """
    author = models.ForeignKey(
        User, 
        verbose_name="Автор рецепта",
        related_name="Subscribers",
        on_delete=models.CASCADE,
    )
    user = models.ForeignKey(
        User,
        verbose_name="Подписчики",
        related_name="Subscriptions",
        on_delete=models.CASCADE,
    )    
    date_sub = models.DateTimeField(
        verbose_name="Дата создания подписки",
        auto_now_add=True,
        editable=False,
    )

    class Meta:
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"
        ordering = ('-id',)
        constraints = [
            UniqueConstraint(fields=["user", "author"],
                             name="unique_subscription")
        ]

    def __str__(self):
        return f"{self.user.username} подписан на {self.author.username}"