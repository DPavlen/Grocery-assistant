from colorfield.fields import ColorField
from django.db import models

from users.models import User

# User = get_user_model()


class Ingredient(models.Model):
    """Ингредиент.
    Один ингредиент может быть у многих рецептов."""
    name = models.CharField(
        verbose_name='Название ингредиента для рецепта',
        max_length=256,
        # required = True
    )
    units = models.CharField(
        verbose_name='Единица измерения',
        max_length=50,
        # required = True
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        # ordering = ['name']

    def __str__(self):
        return self.name


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
        format="hexa",
        default='#FF0000',
        unique=True,
    )
    slug = models.SlugField(
        verbose_name='Slug названия тега',
        max_length=150,
        unique=True,
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
    quantity = models.IntegerField(
        verbose_name='Количество ингредиентов',
        default=1,
    )
    class Meta:
        default_related_name = 'ingridients_recipe'
        verbose_name = 'Ингредиент в рецепте'
        verbose_name_plural = 'Ингредиенты в рецепте'
    
    def __str__(self):
        return f'{self.ingredient} – {self.quantity}'
    

class Recipe(models.Model):
    """Рецепт."""
    author = models.ForeignKey(
        User,
        related_name='recipes',
        on_delete=models.CASCADE,
        verbose_name='Автор публикации рецепта',        
    )
    name = models.CharField(
        verbose_name='Название рецепта',
        max_length=256,
        db_index=True,
    )
    image = models.ImageField(
        verbose_name='Изображение рецепта',
        blank=True,
        upload_to='recipes/images'
    )
    text = models.TextField(
        verbose_name='Описание рецепта',
        help_text='Введите Описание рецепта'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        related_name='recipes',
        verbose_name='Ингредиенты в рецепте',      
    )
    tag = models.ManyToManyField(
        Tag,
        related_name='recipes',
        verbose_name='Теги',      
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
    
    def __str__(self):
        return self.name
    
