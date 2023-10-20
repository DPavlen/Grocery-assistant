from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.fields import SerializerMethodField
from drf_extra_fields.fields import Base64ImageField

from recipes.models import Recipe
from users.models import User, Subscriptions


class ShortRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор короткого рецепта.
    image позволяет передавать изображения в виде base64-строки по API."""

    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            "id",
            "name",
            "image",
            "cooking_time",
        )


class MyUserSerializer(UserSerializer):
    """Сериализатор для просмотра переопределенного Usera и
    проверки просмотра подписок."""

    is_subscribed = SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "password",
            "is_subscribed",
        )
        extra_kwargs = {"password": {"write_only": True}}

    def get_is_subscribed(self, obj):
        """Проверка подписки пользователей.
        Определяет - подписан ли текущий пользователь
        на просматриваемого пользователя."""
        user = self.context.get("request").user
        if user.is_anonymous:
            return False
        return Subscriptions.objects.filter(user=user, author=obj).exists()


class MyUserCreateSerializer(UserCreateSerializer):
    """Сериализатор для создания переопределенного Usera."""

    class Meta:
        model = User
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "password",
        )
        # extra_kwargs = {'password': {'write_only': True}}


class UserSubscriptionsSerializer(serializers.ModelSerializer):
    """Сериализатор для подписок пользователя.
    Выводится текущий пользователь."""

    is_subscribed = SerializerMethodField(read_only=True)
    # recipes = ShortRecipeSerializer(many=True, read_only=True)
    recipes_count = SerializerMethodField()
    recipes = SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
            "recipes",
            "recipes_count",
        )
        read_only_fields = ("email", "username", "first_name", "last_name")

    def get_is_subscribed(self, obj):
        """Проверка подписки пользователей.
        Определяет - подписан ли текущий пользователь
        на просматриваемого пользователя."""

        user = self.context.get("request").user
        if user.is_anonymous:
            return False
        return Subscriptions.objects.filter(user=user, author=obj).exists()

    def get_recipes_count(self, author):
        """Количество рецептов, связанных с текущим автором."""

        return author.recipes.count()

    def get_recipes(self, author):
        """Получить количество рецептов для данного автора."""

        request = self.context.get("request")
        limit = request.GET.get("recipes_limit")
        recipes = (
            author.recipes.all()[: int(limit)]
            if limit
            else author.recipes.all()
        )
        # recipes = author.recipes.all()
        # [: int(limit)] if limit else author.recipes.all()
        serializer = ShortRecipeSerializer(recipes, many=True, read_only=True)
        return serializer.data

    def validate(self, data):
        """Проверка на повторную подписку к существующему пользователю.
        Проверка на подписку самого себя."""

        author = self.instance
        user = self.context.get('request').user
        if Subscriptions.objects.filter(author=author, user=user).exists():
            raise ValidationError('Вы уже подписаны на этого пользователя!')
        if user == author:
            raise serializers.ValidationError(
                'Нельзя подписаться на самого себя!')
        return data
