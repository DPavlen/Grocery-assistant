from django.db.models import F
from django.core.validators import MaxValueValidator, MinValueValidator
from django.forms import ValidationError
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.fields import IntegerField, SerializerMethodField
from rest_framework.relations import PrimaryKeyRelatedField
from drf_extra_fields.fields import Base64ImageField

from core.constants import LenghtField
from recipes.models import (
    Ingredient, Tag, Recipe,
    CompositionOfDish, ShoppingCart, Favorite)
from users.serializers import (
    UserSerializer, MyUserSerializer, MyUserCreateSerializer)


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для получения Тегов."""
    class Meta:
        model = Tag
        fields = (
            'id',
            'name',
            'color',
            'slug',
        )
        read_only_fields = ('__all__',)


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для получения Ингредиентов."""
    class Meta:
        model = Ingredient
        fields = (
            'id',
            'name',
            'measurement_unit',
        )
        read_only_fields = ('__all__',)


class RecipeReadSerializer(serializers.ModelSerializer):
    """Сериализатор для получения Рецептов
    и связанных с ним списка покупок и избранного.Только чтение."""
    tags = TagSerializer(many=True, read_only=True)
    author = MyUserSerializer(read_only=True)
    # author = UserSerializer(read_only=True)
    ingredients = SerializerMethodField()
    image = Base64ImageField()
    is_favorited = SerializerMethodField()
    is_in_shopping_cart = SerializerMethodField()
    cooking_time = serializers.IntegerField(
            validators=[
                MinValueValidator(
                    LenghtField.MIN_COOKING_TIME.value,
                    message=f'Время приготовления блюда должно быть '
                            f'не менее {LenghtField.MIN_COOKING_TIME.value} минуты.'),
                MaxValueValidator(
                    LenghtField.MAX_COOKING_TIME.value,
                    message=f'Время приготовления блюда не превышает '
                            f'более {LenghtField.MAX_COOKING_TIME.value} минут.'),
            ]
        )

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
            # 'is_favorited',
            # 'is_in_shopping_cart',
        )
        read_only_fields = (
            'is_favorite',
            'is_shopping_cart',
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


class CompositionOfDishRecordSerializer(serializers.ModelSerializer):
    """Сериализатор для получения Сотава блюда."""
    id = IntegerField(write_only=True)
    # id = serializers.PrimaryKeyRelatedField(
    #     queryset=Ingredient.objects.all(),
    #     source='ingredient',
    # )
    # amount = serializers.IntegerField(
    #     max_value=LenghtField.MIN_INGREDIENT_VALUE,
    #     min_value=LenghtField.MAX_INGREDIENT_VALUE
    # )

    class Meta:
        model = CompositionOfDish
        fields = (
            'id',
            'amount',
            # 'measurement_unit', 
            # 'amount'
        )


class RecipeRecordSerializer(serializers.ModelSerializer):
    """Сериализатор для получения Рецептов
    и связанных с ним списка покупок и избранного.Запись.
    У одого рецепта может быть несолько связанных тегов(набор)."""
    id = IntegerField(read_only=True)
    tags = PrimaryKeyRelatedField(queryset=Tag.objects.all(),
                                  many=True,)
    # Это User Josera
    # author = UserSerializer(read_only=True)
    author = MyUserSerializer(read_only=True)
    ingredients = CompositionOfDishRecordSerializer(many=True)
    image = Base64ImageField()
    cooking_time = serializers.IntegerField(
            validators=[
                MinValueValidator(
                    LenghtField.MIN_COOKING_TIME.value,
                    message=f'Время приготовления блюда должно быть '
                            f'не менее {LenghtField.MIN_COOKING_TIME.value} минуты.'),
                MaxValueValidator(
                    LenghtField.MAX_COOKING_TIME.value,
                    message=f'Время приготовления блюда не превышает '
                            f'более {LenghtField.MAX_COOKING_TIME.value} минут.'),
            ]
        )

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
        # extra_kwargs = {'tags': {'required': True},
        #                 'ingredients': {'required': True}
        #                 }
    def validate(self, data):
        """Проверяет валидность данных при создании или изменении рецепта.
        Ингредиенты, их количество и повтор ингредиентов"""
        initial_data = self.initial_data
        for field in ('tags', 'ingredients', 'name', 'text', 'cooking_time'):
            if not initial_data.get(field):
                raise ValidationError(f'Не заполнено поле {field}')
        ingredients = initial_data.get('ingredients')
        ingredients_set = set()
        for ingredient in ingredients:
            amount = int(ingredient.get('amount'))
            ingredient_id = ingredient.get('id')
            if not amount or not ingredient_id:
                raise ValidationError(
                    f'Необходимо указать {amount} и {id} ' 
                    f'для создания ингредиента.'
                )
            if not amount > 0:
                raise ValidationError(f'Количество ингредиента {amount} '
                                      'не может быть меньше 1.')
            if ingredient_id in ingredients_set:
                raise ValidationError('Необходимо исключить '
                                      'повторяющиеся ингредиенты.')
            ingredients_set.add(ingredient_id)
        return data

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
        ingredients = validated_data.pop('ingredients', [])
        # Проверка что мы будем создавать рецепт с ингредиентом
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        self.create_composition_of_dish(
            recipe=recipe, ingredients=ingredients)
        return recipe

    def update(self, instance, validated_data):
        """Обновление рецепта."""
        tags = validated_data.pop('tags', [])
        ingredients = validated_data.pop('ingredients', [])
        instance.tags.set(tags)
        instance.ingredients.clear()
        self.create_composition_of_dish(
            recipe=instance, ingredients=ingredients)
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        """Преоразование ингредиентов в словарь с данными
        из списка словарей, в Рецепте."""
        request = self.context.get('request')
        context = {'request': request}
        return RecipeReadSerializer(instance, context=context).data

    def validate_image(self, image):
        if not image:
            raise ValidationError(
                {'image': 'Нужно изображение!'})
        return image

    def validate_ingredients(self, ingredients):
        if not ingredients:
            raise ValidationError(
                {'ingredients': 'Необходим миниму 1 ингердиент!'})
        return ingredients


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


class ShoppingCartSerializer(serializers.Serializer):
    """Добавление и удаление рецептов из корзины покупок."""

    def validate(self, data):
        recipe_id = self.context['recipe_id']
        user = self.context['request'].user
        if ShoppingCart.objects.filter(
            user=user, recipe_id=recipe_id
        ).exists():
            raise serializers.ValidationError(
                'Этот рецепт уже есть в списке покупок'
            )
        return data

    def create(self, validated_data):
        recipe = get_object_or_404(Recipe, pk=validated_data['id'])
        ShoppingCart.objects.create(
            user=self.context['request'].user,
            recipe=recipe
        )
        serializer = ShortRecipeSerializer
        return serializer.data


class FavoritesListSerializer(serializers.Serializer):
    """Сериализатор для добавления рецепта в избранное."""

    def validate(self, data):
        recipe_id = self.context['recipe_id']
        user = self.context['request'].user
        if Favorite.objects.filter(
            user=user, recipe_id=recipe_id
        ).exists():
            raise serializers.ValidationError(
                'Этот рецепт уже есть в избранном'
            )
        return data

    def create(self, validated_data):
        recipe = get_object_or_404(Recipe, pk=validated_data['id'])
        user = self.context['request'].user
        Favorite.objects.create(user=user, recipe=recipe)
        serializer = ShortRecipeSerializer(recipe)
        return serializer.data