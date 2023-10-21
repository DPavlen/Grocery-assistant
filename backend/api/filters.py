from django_filters.rest_framework import FilterSet, filters
from django_filters import FilterSet, ModelMultipleChoiceFilter, NumberFilter


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
        fields = (
            'username',
            'email',
        )


class FilterRecipe(FilterSet):
    """Фильтрация рецептов по тегам. Множественный выбор моделей Tag."""

    is_favorited = NumberFilter(
        field_name='favorites__user',
        method='filter_users_lists', label='is_favorited'
    )
    is_in_shopping_cart = NumberFilter(
        field_name='shoppingcart__user',
        method='filter_users_lists',
        label='is_in_shopping_cart',
    )
    tags = ModelMultipleChoiceFilter(
        field_name='tags__slug',
        queryset=Tag.objects.all(), to_field_name='slug'
    )

    class Meta:
        model = Recipe
        fields = ('tags', 'author', 'is_favorited', 'is_in_shopping_cart')

    def filter_users_lists(self, queryset, name, value):
        user = self.request.user
        if not user.is_authenticated or int(value) == 0:
            return queryset
        return queryset.filter(**{name: user})
