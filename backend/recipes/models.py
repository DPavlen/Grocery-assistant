from colorfield.fields import ColorField
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import UniqueConstraint

from foodgram.settings import MIN_COOKING_TIME, MAX_COOKING_TIME
from recipes.validators import SlugValidator
from users.models import User


class Ingredient(models.Model):
    """Ингредиент.
    Один ингредиент может быть у многих рецептов."""
    name = models.CharField(
        verbose_name='Название ингредиента для рецепта',
        max_length=256,
        # required = True
    )
    measurement_unit = models.CharField(
        verbose_name='Единица измерения',
        max_length=50,
        # required = True
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ['name']

    def __str__(self):
        return f'{self.name}, {self.measurement_unit}'


class Tag(models.Model):
    """Тег рецепта.
    Один тег может быть у многих рецептов."""
    name = models.CharField(
        verbose_name='Название тега для рецепта',
        max_length=256,
        unique=True,
        # required = True
    )
    color = ColorField(
        verbose_name='Цвет в формате HEX',
        format='hex',
        default='#FF0000',
        unique=True,
    )
    slug = models.SlugField(
        verbose_name='Slug названия тега',
        max_length=150,
        unique=True,
        validators=[SlugValidator],
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ['id']

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """Рецепт.Основная модель, у которой есть следующие атрибуты:
    тег рецепта, автор рецепта, ингредиенты рецепта, название рецепта,
    изображение рецепта, описание рецепта, время приготовления блюда."""
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes',
        verbose_name='Теги',
        # required=True
    )
    author = models.ForeignKey(
        User,
        related_name='recipes',
        on_delete=models.CASCADE,
        verbose_name='Автор публикации рецепта',
        # required=True
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        related_name='recipes',
        verbose_name='Состав блюда',
        through='recipes.CompositionOfDish',
        # required=True
    )
    name = models.CharField(
        verbose_name='Название рецепта',
        max_length=256,
        db_index=True,
        # required=True
    )
    image = models.ImageField(
        verbose_name='Изображение рецепта',
        blank=True,
        upload_to='recipes/images',
        help_text='Добавте рецепт',
        # required=True
    )
    text = models.TextField(
        verbose_name='Описание рецепта',
        help_text='Введите Описание рецепта'
        # required=True
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления блюда',
        help_text='Ввведите время приготовления блюда',
        validators=[
            MinValueValidator(
                MIN_COOKING_TIME,
                message=f'Время приготовления блюда должно '
                        f'быть не менее {MIN_COOKING_TIME} минут.'),
            MaxValueValidator(
                MAX_COOKING_TIME,
                message=f'Время приготовления блюда не превышает '
                        f'более {MAX_COOKING_TIME} минут.'),
        ]
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class CompositionOfDish(models.Model):
    """Состав блюда | Ингредиенты в рецепте.
    Определение количества ингредиентов в рецепте.
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
        # related_name='list_of_dish',
        verbose_name='Ингредиенты в рецепте'
    )
    amount = models.SmallIntegerField(
        verbose_name='Количество ингредиентов',
        default=1,
    )

    class Meta:
        # default_related_name = 'composition_of_dish'
        verbose_name = 'Состав блюда | Ингредиент в рецепте'
        verbose_name_plural = 'Состав блюда | Ингредиенты в рецепте'

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
        ordering = ['user',]
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
        related_name='ShoppingCart',
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='ShoppingCart',
        verbose_name='Рецепты пользователей',
    )

    class Meta:
        ordering = ['user',]
        verbose_name = 'Корзина покупок'
        verbose_name_plural = 'Корзина покупок'
        constraints = [
            UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique_shopping_cart',
            )
        ]

    def __str__(self):
        return f'Пользователь {self.user} добавил {self.recipe} в свою Корзину!'
