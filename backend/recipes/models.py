from colorfield.fields import ColorField
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import UniqueConstraint
from django.forms import DateTimeField

from core.constants import LenghtField
from core.validators import SlugValidator, ColorValidator
from users.models import User


class Ingredient(models.Model):
    """Ингредиент.
    Один ингредиент может быть у многих рецептов."""
    name = models.CharField(
        verbose_name='Название ингредиента для рецепта',
        max_length=LenghtField.MAX_LENGT_NAME.value,
    )
    measurement_unit = models.CharField(
        verbose_name='Единица измерения',
        max_length=LenghtField.MAX_LENGT_MEASUREMENT_UNIT.value,
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ['name']
        constraints = [
            UniqueConstraint(fields=['name', 'measurement_unit'],
                             name='unique_measurement_unit')
        ]

    def __str__(self):
        return f'{self.name}, {self.measurement_unit}'


class Tag(models.Model):
    """Тег рецепта.
    Один тег может быть у многих рецептов."""
    name = models.CharField(
        verbose_name='Название тега для рецепта',
        max_length=LenghtField.MAX_LENGT_NAME.value,
        unique=True,
    )
    color = ColorField(
        verbose_name='Цвет в формате HEX',
        max_length=LenghtField.MAX_LENGT_NAME_COLOR.value,
        format='hex',
        default='#FF0000',
        unique=True,
        validators=[ColorValidator],
    )
    slug = models.SlugField(
        verbose_name='Slug названия тега',
        max_length=LenghtField.MAX_LENGT_NAME_SLUG.value,
        unique=True,
        validators=[SlugValidator],
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ['id']
        constraints = [
            UniqueConstraint(
                fields=('name', 'slug'),
                name='unique_slug_in_name',
            )
        ]

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """Рецепт.Основная модель, у которой есть следующие атрибуты:
    тег рецепта, автор рецепта, ингредиенты рецепта, название рецепта,
    изображение рецепта, описание рецепта, время приготовления блюда.
    """
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes',
        verbose_name='Теги',
    )
    author = models.ForeignKey(
        User,
        related_name='recipes',
        on_delete=models.CASCADE,
        verbose_name='Автор публикации рецепта',
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        related_name='recipes',
        verbose_name='Состав блюда',
        through='recipes.CompositionOfDish',
    )
    name = models.CharField(
        verbose_name='Название рецепта',
        max_length=LenghtField.MAX_LENGT_NAME.value,
        db_index=True,
    )
    image = models.ImageField(
        verbose_name='Изображение рецепта',
        upload_to='recipes/images',
        help_text='Добавьте рецепт',
    )
    text = models.TextField(
        verbose_name='Описание рецепта',
        help_text='Введите Описание рецепта'
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления блюда',
        help_text='Ввведите время приготовления блюда',
        validators=[
            MinValueValidator(
                LenghtField.MIN_COOKING_TIME.value,
                message=f'Время приготовления блюда должно быть '
                        f'не менее {LenghtField.MIN_COOKING_TIME.value} минут.'),
            MaxValueValidator(
                LenghtField.MAX_COOKING_TIME.value,
                message=f'Время приготовления блюда не превышает '
                        f'более {LenghtField.MAX_COOKING_TIME.value} минут.'),
        ]
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации рецепта',
        auto_now_add=True
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-pub_date',)

    def __str__(self):
        return self.name


class CompositionOfDish(models.Model):
    """Состав блюда | Ингредиенты в рецепте.
    Определение количества ингредиентов в рецепте.
    Ограничение: В рецепте уникальный ингредиент.
    """
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='composition_list',
        verbose_name='Рецепты',
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингредиенты в рецепте'
    )
    amount = models.SmallIntegerField(
        verbose_name='Количество ингредиентов',
        default=1,
        validators=[
            MinValueValidator(
                LenghtField.MIN_AMOUNT_INREDIENT.value,
                message=f'Минимальное количество ингредиетов в блюде '
                        f'должно быть не меньше '
                        f'{LenghtField.MIN_AMOUNT_INREDIENT.value}.'),
            MaxValueValidator(
                LenghtField.MAX_AMOUNT_INREDIENT.value,
                message=f'Максимально количество ингредиетов в блюде '
                        f'не превышает {LenghtField.MAX_AMOUNT_INREDIENT.value}.'),
        ]
    )

    class Meta:
        verbose_name = 'Состав блюда | Ингредиент в рецепте'
        verbose_name_plural = 'Состав блюда | Ингредиенты в рецепте'
        constraints = [
            UniqueConstraint(
                fields=('recipe', 'ingredient'),
                name='unique_ingredient_in_recipe',
            )
        ]


    def __str__(self):
        return f'{self.ingredient} – {self.amount}'


class Favorite(models.Model):
    """Избранные рецепты у пользователей."""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Пользователи',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Рецепты пользователей',
    )

    class Meta:
        ordering = ['user']
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранное'
        constraints = [
            UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique_favourites',
            )
        ]

    def __str__(self):
        return f'Пользователь {self.user} добавил {self.recipe} в Избранное!'


class ShoppingCart(models.Model):
    """Корзина покупок у пользователей."""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shoppingcart',
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shoppingcart',
        verbose_name='Рецепты пользователей',
    )

    class Meta:
        ordering = ['user']
        verbose_name = 'Корзина покупок'
        verbose_name_plural = 'Корзина покупок'
        constraints = [
            UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique_shopping_cart',
            )
        ]

    def __str__(self):
        return f'Пользователь {self.user} добавил {self.recipe} в Корзину!'
