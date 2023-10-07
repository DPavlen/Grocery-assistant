from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, SAFE_METHODS
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from api.pagination import PaginationCust
from api.permissions import IsAdminOrReadOnly, IsAdminAuthorOrReadOnly
from api.serializers import ( TagSerializer, IngredientSerializer, 
    RecipeReadSerializer,RecipeRecordSerializer, ShortRecipeSerializer)
from recipes.models import (
    Ingredient, Tag, Recipe, Favorite, ShoppingCart)


class TagViewSet(ReadOnlyModelViewSet):
    """Работа с Тегами. Получить список всех тегов.
    Изменение и создание тэгов разрешено только админам."""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (IsAdminOrReadOnly,)


class IngredientViewSet(ReadOnlyModelViewSet):
    """Работа с Тегами. Получить список всех тегов.
     Изменение и создание тэгов разрешено только админам."""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (IsAdminOrReadOnly,)
    pagination_class = PaginationCust


class RecipeViewSet(ModelViewSet):
    """Работа с рецептами. Отображение избранного, списка покупок.
    RecipeViewSet отрабатывает по 2 сериализаторам:Чтение и запись."""
    queryset = Recipe.objects.all()
    # permission_classes = (IsAdminAuthorOrReadOnly)
    pagination_class = PaginationCust
    # filter_backends

    def perform_create(self, serializer, **kwargs):
        serializer.save(author=self.request.user)

    def get_serializer_class(self):
        return (RecipeReadSerializer if self.request.method in SAFE_METHODS
                else RecipeRecordSerializer)

    @action(
        detail=True,
        methods=['post'],
        permission_classes=[IsAuthenticated],
    )
    def favorite(self, request, pk):
        """Добавление рецептов в раздел Избранное."""
        return self.add_recipe(Favorite, request.user, pk)
    
    @favorite.mapping.delete
    def delete_favorite(self, request, pk):
        """Удаление рецептов из раздела Избранное."""    
        return self.delete_recipe(Favorite, request.user, pk)

    @action(
        detail=True,
        methods=['post'],
        permission_classes=[IsAuthenticated],
    )
    def shopping_сart(self, request, pk):
        """Добавление рецептов в раздел Корзина покупок."""
        return self.add_recipe(ShoppingCart, request.user, pk)
    
    @shopping_сart.mapping.delete
    def delete_shopping_сart(self, request, pk):
        """Удаление рецептов в раздел Корзина покупок."""
        return self.delete_recipe(ShoppingCart, request.user, pk)

    def add_recipe(self, models, user, pk):
        """Метод добавления рецептов."""
        recipe = get_object_or_404(Recipe, id=pk)
        if models.objects.filter(user=user, recipe=recipe).exists():
            return Response({'Ошибка': 'Рецепт уже добавлен!'},
                        status=status.HTTP_400_BAD_REQUEST)
        models.objects.create(user=user, recipe=recipe)
        serializer = ShortRecipeSerializer(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete_recipe(self, models, user, pk):
        """Метод удаления рецепта."""
        obj = get_object_or_404(models, user=user, recipe__id=pk)
        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    
