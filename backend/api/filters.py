from django_filters.rest_framework import FilterSet, filters

from recipes.models import Ingredient, Tag, Recipe, User


class FilterIngredient(FilterSet):
    """Фильтр для модели Ингредиент по полю name."""
    name = filters.CharFilter(lookup_expr='startswith')

    class Meta:
        model = Ingredient
        fields = ('name',)


class FilterUser(FilterSet):
    """Фильтр для модели Юзеров по полям username, email."""
    username = filters.CharFilter(lookup_expr='startswith')
    email = filters.CharFilter(lookup_expr='startswith')

    class Meta:
        model = User
        fields = ('username', 'email',)


class FilterRecipe(FilterSet):
    """Фильтрация рецептов по тегам. Множественный выбор моделей Tag."""
    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all(),
    )
    is_favorited = filters.NumberFilter(method='filter_is_favorited')
    is_in_shopping = filters.NumberFilter(
        method='filte_is_in_shopping_cart'
    )

    class Meta:
        model = Recipe
        fields = (
            'tags',
            'author',
            'is_favorited',
            'is_in_shopping',
        )

    def filter_is_favorited(self, queryset, name, value):
        """Фильтрует Recipe по тому, является ли конкретный
        рецепт избранным для определенного пользователя,
        на основе переданных значений value"""

        if value and self.request.user.is_authenticated:
            return queryset.filter(favorites__user=self.request.user)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        """Фильтрует Recipe по тому, находится ли конкретный рецепт
        в корзине покупок для определенного пользователя,
        на основе переданных значений value."""

        if value and self.request.user.is_authenticated:
            return queryset.filter(shopping_list__user=self.request.user)
        return
