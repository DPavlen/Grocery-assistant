from django.db.models import F
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.fields import IntegerField, SerializerMethodField
from rest_framework.relations import PrimaryKeyRelatedField
from drf_extra_fields.fields import Base64ImageField

from core.constants import Lenght
from recipes.models import (
    Ingredient, Tag, Recipe, 
    CompositionOfDish, ShoppingCart, Favorite)
from users.serializers import UserSerializer


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для получения Тегов."""
    class Meta:
        model = Tag
        fields = (
            'id',
            'name',
            'slug',
            'color',
        )


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для получения Ингредиентов."""
    class Meta:
        model = Ingredient
        fields = (
            'id',
            'name',
            'measurement_unit',
        )


class RecipeReadSerializer(serializers.ModelSerializer):
    """Сериализатор для получения Рецептов
    и связанных с ним списка покупок и избранного.Только чтение."""
    tags = TagSerializer(many=True, read_only=True)
    author = UserSerializer(read_only=True)
    ingredients = SerializerMethodField()
    image = Base64ImageField()
    is_favorited = SerializerMethodField()
    is_in_shopping_cart = SerializerMethodField()
    cooking_time = SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'image',
            'text',
            'cooking_time',
            'is_favorited',
            'is_in_shopping_cart',
        )

    def get_ingredients(self, obj):
        """Получает список ингридиентов для рецепта."""
        recipe = obj
        ingredients = recipe.ingredients.values(
            'id',
            'name',
            'measurement_unit',
            amount=F('compositionofdish__amount'),
        )
        return ingredients

    def get_is_favorited(self, recipe):
        """Проверка - находится ли рецепт в избранном."""
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Favorite.objects.filter(user=user, recipe=recipe).exists()

    def get_is_in_shopping_cart(self, recipe):
        """Проверка - находится ли рецепт в списке  покупок."""
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return ShoppingCart.objects.filter(user=user, recipe=recipe).exists()

    def get_cooking_time(self, recipe):
        """Проверка на время приготовления."""
        if recipe.cooking_time < Lenght.MIN_COOKING_TIME.value:
            raise serializers.ValidationError(
                f'Время приготовления блюда должно быть не менее '
                f'{Lenght.MIN_COOKING_TIME.value} минут.')
        elif recipe.cooking_time > Lenght.MAX_COOKING_TIME.value:
            raise serializers.ValidationError(
                f'Время приготовления блюда не должно превышать ' 
                f'{Lenght.MAX_COOKING_TIME.value} минут.')
        return recipe.cooking_time


class CompositionOfDishRecordSerializer(serializers.ModelSerializer):
    """Сериализатор для получения Сотава блюда."""
    id = IntegerField(write_only=True)

    class Meta:
        model = CompositionOfDish
        fields = (
            'id',
            'amount',
        )


class RecipeRecordSerializer(serializers.ModelSerializer):
    """Сериализатор для получения Рецептов
    и связанных с ним списка покупок и избранного.Запись.
    У одого рецепта может быть несолько связанных тегов(набор)."""
    id = IntegerField(read_only=True)
    tags = PrimaryKeyRelatedField(queryset=Tag.objects.all(),
                                  many=True)
    author = UserSerializer(read_only=True)
    ingredients = CompositionOfDishRecordSerializer(many=True)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'ingredients',
            'author',
            'name',
            'image',
            'text',
            'cooking_time',
        )

    def create_composition_of_dish(self, ingredients, recipe):
        """Cоздание связей между ингредиентами и рецептом.
        Входные параметры данной функции включают список
        ингредиентов (ingredients) и рецепт (recipe)."""
        compositions = []
        for ingredient in ingredients:
            composition = CompositionOfDish(
                ingredient=Ingredient.objects.get(id=ingredient['id']),    
                recipe=recipe,
                amount=ingredient['amount']
            )
            compositions.append(composition)
        CompositionOfDish.objects.bulk_create(compositions)

    def create(self, validated_data):
        """Создание рецепта с указанными полями.
        Получаем данные о тегах и ингредиентах.
        Создаем рецепт и связываем с тегом."""
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients',[])
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        self.create_composition_of_dish(recipe=recipe, ingredients=ingredients)
        return recipe


    def update(self, instance, validated_data):
        """Обновление рецепта."""
        tags = validated_data.pop('tags', [])
        ingredients = validated_data.pop('ingredients', [])
        instance.tags.set(tags)
        instance.ingredients.clear()
        self.create_composition_of_dish(
            recipe=instance, ingredients=ingredients)
        instance = super().update(instance, validated_data)
        instance.save()
        return instance

    
    def to_representation(self, instance):
        """Преоразование ингредиентов в словарь с данными
        из списка словарей, в Рецепте."""
        request = self.context.get('request')
        context = {'request': request}
        return RecipeReadSerializer(instance, context=context).data
    

class ShortRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор короткого рецепта.
    image позволяет передавать изображения в виде base64-строки по API."""
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time',
        )
