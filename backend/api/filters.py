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


# class FilterRecipe(FilterSet):
#     """Фильтрация рецептов по тегам. Множественный выбор моделей Tag."""
#     tags = filters.ModelMultipleChoiceFilter(
#         field_name='tags__slug',
#         to_field_name='slug',
#         queryset=Tag.objects.all(),
#     )
#     # is_favorited = filters.NumberFilter(method='filter_is_favorited')
#     # is_in_shopping = filters.NumberFilter(
#     #     method='filte_is_in_shopping_cart'
#     # )
#     is_favorited = filters.BooleanFilter(
#         method='filter_is_favorited',
#         label='is_favorited',
#     )
#     is_in_shopping_cart = filters.BooleanFilter(
#         method='filter_is_in_shopping_cart',
#         label='is_in_shopping_cart',
#     )

#     class Meta:
#         model = Recipe
#         fields = (
#             'tags',
#             'author',
#             'is_favorited',
#             'is_in_shopping_cart',
#         )

#     def filter_is_favorited(self, queryset, name, value):
#         """Фильтрует Recipe по тому, является ли конкретный
#         рецепт избранным для определенного пользователя,
#         на основе переданных значений value"""

#         if value and self.request.user.is_authenticated:
#             return queryset.filter(favorites__user=self.request.user)
#         return queryset

#     def filter_is_in_shopping_cart(self, queryset, name, value):
#         """Фильтрует Recipe по тому, находится ли конкретный рецепт
#         в корзине покупок для определенного пользователя,
#         на основе переданных значений value."""

#         if value and self.request.user.is_authenticated:
#             return queryset.filter(shoppingcart__user=self.request.user)
#         return queryset


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
