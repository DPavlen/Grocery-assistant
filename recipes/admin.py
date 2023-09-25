from django.contrib import admin

from recipes.models import Ingredient, Tag, Recipe, IngredientInRecipe



@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """Настроенная админ-панель Ингридентов."""
    list_display = ('id', 'name', 'units')
    search_fields = ('name',)
    list_filter = ('name', 'units')


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Настроенная админ-панель Тегов."""
    list_display = (
        'id',
        'name',
        'color',
        'slug',
    )
    search_fields = ('name',)
    list_filter = ('id', 'name', 'color')


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """Настроенная админ-панель Тегов."""
    list_display = (
        'id',
        'author',
        'name',
        'image',
        'text'
    )
    search_fields = ('author',)
    list_filter = ('id', 'author', 'name')

    
@admin.register(IngredientInRecipe)
class IngredientInRecipeAdmin(admin.ModelAdmin):
    """Настроенная админ-панель Ингредиенты в рецепте."""
    list_display = (
        'id',
        'ingredient',
        'quantity',
    )
    search_fields = ('ingredient',)
    list_filter = ('id', 'ingredient', 'quantity')