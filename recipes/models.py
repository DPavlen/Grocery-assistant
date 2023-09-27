from colorfield.fields import ColorField
from django.db import models
from django.db.models import UniqueConstraint

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
        #max_length=7,
        format='hexa',
        default='#FF0000',
        unique=True,
    )
    slug = models.SlugField(
        verbose_name='Slug названия тега',
        max_length=150,
        unique=True,
        # Валидация ^[-a-zA-Z0-9_]+$
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ['id']
    
    def __str__(self):
        return self.name 

    
class IngredientInRecipe(models.Model):
    """Ингредиенты в рецепте.
    Определение количества ингредиентов в рецепте.
    """
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='list_of_ingredient',
        verbose_name='Ингредиенты в рецепте'
    )
    amount = models.IntegerField(
        verbose_name='Количество ингредиентов',
        default=1,
    )
    class Meta:
        default_related_name = 'ingridients_recipe'
        verbose_name = 'Ингредиент в рецепте'
        verbose_name_plural = 'Ингредиенты в рецепте'
    
    def __str__(self):
        return f'{self.ingredient} – {self.amount}'
    

class Recipe(models.Model):
    """Рецепт.Основная модель, у которой есть следующие атрибуты:
    тег рецепта, автор рецепта, ингредиенты рецепта, название рецепта,
    изображение рецепта, описание рецепта, время приготовления блюда."""
    tag = models.ManyToManyField(
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
        IngredientInRecipe,
        related_name='recipes',
        verbose_name='Ингредиенты в рецепте',
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
    cooking_time = models.SmallIntegerField(
        verbose_name='Время приготовления блюда',
        help_text='Ввведите время приготовления'
        # required=True 
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
    
    def __str__(self):
        return self.name


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