import io
from django.forms import ValidationError
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
#
from reportlab.pdfgen import canvas
from tkinter import Canvas
from django.db.models import Sum
#
from rest_framework.exceptions import PermissionDenied
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import (
    IsAuthenticated, SAFE_METHODS, IsAuthenticatedOrReadOnly)
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from api.filters import FilterIngredient, FilterRecipe
from api.pagination import PaginationCust
from api.permissions import IsAdminOrReadOnly, IsAuthorOrAdminOrIsAuthReadOnly
from api.serializers import (TagSerializer, IngredientSerializer,
                             RecipeReadSerializer, RecipeRecordSerializer,
                             ShortRecipeSerializer, ShoppingCartSerializer,
                             FavoritesListSerializer)
from core.utils import create_shopping_list_report
from recipes.models import (
    Ingredient, Tag, Recipe, Favorite, ShoppingCart, CompositionOfDish)


class TagViewSet(ReadOnlyModelViewSet):
    """Работа с Тегами. Получить список всех тегов.
    Изменение и создание тэгов разрешено только админам."""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(ReadOnlyModelViewSet):
    """Работа с Тегами. Получить список всех тегов.
     Изменение и создание тэгов разрешено только админам."""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = FilterIngredient
    pagination_class = None


class RecipeViewSet(ModelViewSet):
    """Работа с рецептами. Отображение избранного, списка покупок.
    RecipeViewSet отрабатывает по 2 сериализаторам:Чтение и запись."""
    queryset = Recipe.objects.all()
    # permission_classes = (IsAuthorOrAdminOrIsAuthReadOnly | IsAdminOrReadOnly,)
    permission_classes = (IsAuthenticatedOrReadOnly,)
    pagination_class = PaginationCust
    filter_backends = (DjangoFilterBackend,)
    filterset_class = FilterRecipe

    # def perform_create(self, serializer, **kwargs):
    #     serializer.save(author=self.request.user)
    def get_serializer_class(self):
        # return (RecipeReadSerializer if self.request.method in SAFE_METHODS
                # else RecipeRecordSerializer)
    
        if self.action in SAFE_METHODS:
            return RecipeReadSerializer
        elif self.action == 'favorite':
            return FavoritesListSerializer
        elif self.action == 'shopping_cart':
            return ShoppingCartSerializer
        return RecipeRecordSerializer
    

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    
    # def get_serializer_class(self):
    #     return (RecipeReadSerializer if self.request.method in SAFE_METHODS
    #             else RecipeRecordSerializer)
    
    def perform_update(self, serializer):
        serializer.save(author=self.request.user)

    # def partial_update(self, request, *args, **kwargs):
    #     request._request.PUT = request._request.PATCH
    #     return self.update(request, *args, **kwargs)
    
    # def partial_update(self, request, *args, **kwargs):
        
    #     kwargs['partial'] = False
    #     return self.update(request, *args, **kwargs)
    def destroy(self, request, *args, **kwargs):
        """Проверяем, является ли пользователь автором рецепта.
        И если нет, то не даем удалять чужой рецепт."""
        instance = self.get_object()
        if instance.author != request.user:
            raise PermissionDenied("Вы не можете удалить чужой рецепт")
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=['post'],
        serializer_class=FavoritesListSerializer,
        permission_classes=[IsAuthenticated]
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
        serializer_class=ShoppingCartSerializer,
        permission_classes=[IsAuthenticated]
    )
    def shopping_сart(self, request,  pk):
        """Добавление рецептов в раздел Корзина покупок."""
        return self.add_recipe(ShoppingCart, request.user, pk)

    @shopping_сart.mapping.delete
    def delete_shopping_сart(self, request, pk):
        if not request.user.is_authenticated:
            return Response(status=status.HTTP_401_UNAUTHORIZED,
                        data={'detail': 'User is not authenticated.'})
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
        try:
            obj = get_object_or_404(models, user=user, recipe__id=pk)
            obj.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except models.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST, 
                            data={'detail': 'Not found.'})

    @action(
        detail=False,
        methods=('get',),
        permission_classes=[IsAuthenticated],
    )
    def download_shopping_cart(self, request):
        """
        Получение списка покупок у текущего
        пользователя из базы данных.
        Использует этот буфер для создания HTTP-ответа с прикрепленным PDF-файлом.
        """
        user = self.request.user
        if not user.ShoppingCart.exists():
            return Response(status=status.HTTP_400_BAD_REQUEST)
        shopping_cart = ShoppingCart.objects.filter(user=request.user)
        buy_list_text = create_shopping_list_report(shopping_cart)
        # Создание HttpResponse с содержимым буфера
        response = HttpResponse(
            buy_list_text,
            content_type='application/pdf'
        )
        pdf_filename = 'shopping_cart.pdf'
        response['Content-Disposition'] = f'attachment; filename="{pdf_filename}"'
        return response
 