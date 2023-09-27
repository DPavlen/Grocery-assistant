from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin

from recipes.models import (Ingredient, Tag, Recipe, IngredientInRecipe, 
                            Favorite, ShoppingCart)



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
        'text',
        #'ingredient',
        #'tags',
        'cooking_time'
    )
    search_fields = ('author',)
    list_filter = ('id', 'author', 'name')


@admin.register(IngredientInRecipe)
class IngredientInRecipeAdmin(admin.ModelAdmin):
    """Настроенная админ-панель Ингредиенты в рецепте."""
    list_display = (
        'id',
        'ingredient',
        'amount',
    )
    search_fields = ('ingredient',)
    list_filter = ('id', 'ingredient', 'amount')



class IngredientResource(resources.ModelResource):
    class Meta:
        model = Ingredient
        fields = (
            'id',
            'ingredient',
            'amount',
        )


class IngredientAdmin(ImportExportModelAdmin):
    resource_classes = [IngredientResource]

admin.site.register(Ingredient, IngredientAdmin)


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    """Настроенная админ-панель избранные рецепты у пользователей."""
    list_display = (
        'user', 
        'recipe'
    )
    list_filter = ('user', 'recipe')
    search_fields = ('user', 'recipe')


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    """Настроенная админ-панель корзин покупок у пользователей."""
    list_display = (
        'recipe', 
        'user'
    )
    list_filter = ('recipe', 'user')
    search_fields = ('user',)