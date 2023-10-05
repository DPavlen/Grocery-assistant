from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db.models import F
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.fields import IntegerField, SerializerMethodField
from rest_framework.relations import PrimaryKeyRelatedField
from drf_extra_fields.fields import Base64ImageField

from recipes.models import (
    Ingredient, Tag, Recipe, Favorite, ShoppingCart,CompositionOfDish)
from users.models import User, Subscriptions


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для создания переопределенного Usera и
    проверки просмотра подписок."""
    is_subscribed = SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'password',
        )
        # поле "password" будет доступно только для записи 
        extra_kwargs = {'password': {'write_only': True}}
                        

    def create(self, validated_data):
        """Создание нового пользователя с указанными полями."""
        user = User(
            username=validated_data['username'],
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
        )
        user.set_password(validated_data['password'])
        user.save()
        return user
    
    
    def get_is_subscribed(self, author):
        """Проверка подписки пользователей. Определяет - подписан ли текущий пользователь
        на просматриваемого пользователя(True or False)."""
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Subscriptions.objects.filter(user=user, author=author).exists()
    

class UserSubscriptionsSerializer(serializers.ModelSerializer):
    """Сериализатор для подписок пользователя. 
    Выводится текущий пользователь."""
    recipes_count = SerializerMethodField()
    recipes = SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'recipes',
            'recipes_count',
        )


    def get_recipes(self, author):
        """Количество рецептов, связанных с текущим автором."""
        return author.recipes.count()
    

    def get_recipes_count(self, author):
        """Получить количество рецептов для данного автора."""
        request = self.context.get('request')
        limit = request.GET.get('recipes_limit')
        recipes = author.recipes.all()[:int(limit)] if limit else author.recipes.all()
        serializer = ShortRecipeSerializer(recipes, many=True, read_only= True)
        return serializer.data
    
    def validate(self, data):
        """Проверка на повторную подписку к существующему пользователю.
        Проверка на подписку самого себя."""
        author = self.instance
        user = self.context.get('request').user
        if Subscriptions.objects.filter(author=author, user=user).exists():
            raise ValidationError(
                'Вы уже подписаны на этого пользователя себя!'
                )
        if user == author:
            raise serializers.ValidationError(
                'Нельзя подписаться на самого себя!'
            )
        return data
    


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
        return user.favorites.filter(recipe=recipe).exists()
        # return not user.is_anonymous and user.favorites.filter(recipe=recipe).exists()


    def get_is_in_shopping_cart(self, recipe):
        """Проверка - находится ли рецепт в списке  покупок."""
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return user.carts.filter(recipe=recipe).exists()
    

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

    def create_composition_of_dish(self, recipe, ingredients):
        """Cоздание связей между ингредиентами и рецептом. 
        Входные параметры данной функции включают список
        ингредиентов (ingredients) и рецепт (recipe)."""
        compositions = []
        # Проверяем, что список ingredients не пустой
        if ingredients:
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
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        self.create_composition_of_dish(recipe=recipe, ingredients=ingredients)
        return recipe


    def update(self, instance, validated_data):
        """Обновление рецепта."""
        tags = validated_data.pop('tags', [])
        ingredients = validated_data.pop('ingredients', [])
        instance = super().update(instance, validated_data)
        instance.tags.set(tags)
        instance.ingredients.clear()
        self.create_composition_of_dish(recipe=instance, ingredients=ingredients)
        instance.save()
        return instance
        
    