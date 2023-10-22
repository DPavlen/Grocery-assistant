from django.db.models import F
from django.core.validators import MaxValueValidator, MinValueValidator
from django.forms import ValidationError
from rest_framework import serializers
from rest_framework.fields import IntegerField, SerializerMethodField
from rest_framework.relations import PrimaryKeyRelatedField
from drf_extra_fields.fields import Base64ImageField

from core.constants import LenghtField
from recipes.models import (
    CompositionOfDish,
    Ingredient,
    Favorite,
    Recipe,
    ShoppingCart,
    Tag,
)
from users.serializers import MyUserSerializer


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для получения Тегов."""

    class Meta:
        model = Tag
        fields = (
            "id",
            "name",
            "color",
            "slug",
        )
        read_only_fields = ("__all__",)


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для получения Ингредиентов."""

    class Meta:
        model = Ingredient
        fields = (
            "id",
            "name",
            "measurement_unit",
        )
        read_only_fields = ("__all__",)


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
                message=f"Время приготовления блюда должно быть "
                f"не менее {LenghtField.MIN_COOKING_TIME.value} минуты.",
            ),
            MaxValueValidator(
                LenghtField.MAX_COOKING_TIME.value,
                message=f"Время приготовления блюда не превышает "
                f"более {LenghtField.MAX_COOKING_TIME.value} минут.",
            ),
        ]
    )

    class Meta:
        model = Recipe
        fields = (
            "id",
            "tags",
            "author",
            "ingredients",
            "is_favorited",
            "is_in_shopping_cart",
            "name",
            "image",
            "text",
            "cooking_time",
        )
        read_only_fields = (
            "is_favorite",
            "is_shopping_cart",
        )

    def get_ingredients(self, obj):
        """Получает список ингридиентов для рецепта."""
        recipe = obj
        ingredients = recipe.ingredients.values(
            "id",
            "name",
            "measurement_unit",
            amount=F("compositionofdish__amount"),
        )
        return ingredients

    def get_is_favorited(self, recipe):
        """Проверка - находится ли рецепт в избранном."""
        user = self.context.get("request").user
        if user.is_anonymous:
            return False
        return Favorite.objects.filter(user=user, recipe=recipe).exists()

    def get_is_in_shopping_cart(self, recipe):
        """Проверка - находится ли рецепт в списке  покупок."""
        user = self.context.get("request").user
        if user.is_anonymous:
            return False
        return ShoppingCart.objects.filter(user=user, recipe=recipe).exists()


class CompositionOfDishRecordSerializer(serializers.ModelSerializer):
    """Сериализатор для получения Сотава блюда."""

    id = IntegerField(write_only=True)

    class Meta:
        model = CompositionOfDish
        fields = (
            "id",
            "amount",
        )


class RecipeRecordSerializer(serializers.ModelSerializer):
    """Сериализатор для получения Рецептов
    и связанных с ним списка покупок и избранного.Запись.
    У одого рецепта может быть несолько связанных тегов(набор)."""

    id = IntegerField(read_only=True)
    tags = PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True,
    )
    author = MyUserSerializer(read_only=True)
    ingredients = CompositionOfDishRecordSerializer(many=True)
    image = Base64ImageField()
    cooking_time = serializers.IntegerField(
        validators=[
            MinValueValidator(
                LenghtField.MIN_COOKING_TIME.value,
                message=f"Время приготовления блюда должно быть "
                f"не менее {LenghtField.MIN_COOKING_TIME.value} минуты.",
            ),
            MaxValueValidator(
                LenghtField.MAX_COOKING_TIME.value,
                message=f"Время приготовления блюда не превышает "
                f"более {LenghtField.MAX_COOKING_TIME.value} минут.",
            ),
        ]
    )

    class Meta:
        model = Recipe
        fields = (
            "id",
            "tags",
            "ingredients",
            "author",
            "name",
            "image",
            "text",
            "cooking_time",
        )

    def validate(self, data):
        """Дополнительные проверки наличия и количества
        ингредиентов и тегов в рецепте
        (уникальность, наличие и прочее.)."""

        # Проверка на наличие тегов.
        tags = data.get("tags", [])
        if not tags:
            raise serializers.ValidationError(
                {"tags": "Укажите хотя бы один тег."})

        # Проверка на наличие ингредиентов в рецепте.
        ingredients = data.get("ingredients", [])
        if not ingredients:
            raise serializers.ValidationError(
                {"ingredients":
                 "Укажите хотя бы один ингредиент."}
            )

        # Проверка на уникальность тегов.
        tag_ids = [tag.id for tag in tags]
        if len(tag_ids) != len(set(tag_ids)):
            raise serializers.ValidationError(
                {"tags": "Теги не могут дублироваться."})

        # Проверка на уникальность ингредиентов в рецепте.
        ingredient_ids = [ingredient["id"] for ingredient in ingredients]
        if len(ingredient_ids) != len(set(ingredient_ids)):
            raise serializers.ValidationError(
                {"ingredients":
                 "Ингредиенты не могут дублироваться."}
            )

        # Дополнительная проверка ингредиентов на минимальное количество.
        if len(ingredients) < 1:
            raise ValidationError(
                {"ingredients": f"Нужен минимум " f"{1} ингредиент!"})

        # Проверка на пустое поле тегов в рецепте.
        if not data.get("tags"):
            raise serializers.ValidationError(
                {"tags": "Поле тегов не может быть пустым."}
            )

        # Проверка на пустое поле ингредиентов в рецепте.
        if not data.get("ingredients"):
            raise serializers.ValidationError(
                {"ingredients":
                 "Поле ингредиентов не может быть пустым."}
            )

        return data

    def create_composition_of_dish(self, ingredients, recipe):
        """Cоздание связей между ингредиентами и рецептом.
        Входные параметры данной функции включают список
        ингредиентов (ingredients) и рецепт (recipe)."""
        compositions = []
        for ingredient in ingredients:
            composition = CompositionOfDish(
                ingredient=Ingredient.objects.get(id=ingredient["id"]),
                recipe=recipe,
                amount=ingredient["amount"],
            )
            compositions.append(composition)
        CompositionOfDish.objects.bulk_create(compositions)

    def create(self, validated_data):
        """Создание рецепта с указанными полями.
        Получаем данные о тегах и ингредиентах.
        Создаем рецепт и связываем с тегом."""
        tags = validated_data.pop("tags")
        ingredients = validated_data.pop("ingredients", [])
        # Проверка на несуществующий ингредиент в рецепте
        for ingredient in ingredients:
            ingredient = ingredient["id"]
            try:
                Ingredient.objects.get(id=ingredient)
            except Ingredient.DoesNotExist:
                raise serializers.ValidationError(
                    {
                        "Ingredients": f"Такого ингредиента id="
                        f"{ingredient} не существует!"
                    }
                )
        # Проверка что мы будем создавать рецепт с ингредиентом
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        self.create_composition_of_dish(
            recipe=recipe, ingredients=ingredients)
        return recipe

    def update(self, instance, validated_data):
        """Обновление рецепта."""
        tags = validated_data.pop("tags", [])
        ingredients = validated_data.pop("ingredients", [])
        # Проверка на несуществующий ингредиент в рецепте
        for ingredient in ingredients:
            ingredient = ingredient["id"]
            try:
                Ingredient.objects.get(id=ingredient)
            except Ingredient.DoesNotExist:
                raise serializers.ValidationError(
                    {
                        "Ingredients": f"Такого ингредиента id="
                        f"{ingredient} не существует!"
                    }
                )
        instance.tags.set(tags)
        instance.ingredients.clear()
        self.create_composition_of_dish(
            recipe=instance, ingredients=ingredients)
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        """Преоразование ингредиентов в словарь с данными
        из списка словарей, в Рецепте."""
        request = self.context.get("request")
        context = {"request": request}
        return RecipeReadSerializer(
            instance, context=context).data

    def validate_image(self, image):
        if not image:
            raise ValidationError({"image": "Нужно изображение!"})
        return image

    def validate_ingredients(self, ingredients):
        if not ingredients:
            raise ValidationError(
                {"ingredients": "Необходим миниму 1 ингердиент!"})
        return ingredients


class ShortRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор короткого рецепта. Image позволяет
    передавать изображения в виде base64-строки по API."""

    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            "id",
            "name",
            "image",
            "cooking_time",
        )
