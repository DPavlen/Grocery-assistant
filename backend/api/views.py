from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, SAFE_METHODS
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from .pagination import PaginationCust
from .permissions import IsAdminOrReadOnly, IsAdminAuthorOrReadOnly
from .serializers import (
    UserSerializer, TagSerializer, IngredientSerializer, UserSubscriptionsSerializer,
    RecipeReadSerializer, RecipeRecordSerializer, ShortRecipeSerializer
)
from recipes.models import (
    Ingredient, Tag, Recipe, Favorite, ShoppingCart)
from users.models import User, Subscriptions


class CustomUserViewSet(UserViewSet):
    """Работа с пользователями. Регистрация пользователей.
    Вывод пользователей. У авторизованных пользователей 
    возможность подписки. Djoser позволяет переходить 
    по endpoints user и токена."""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAdminOrReadOnly,)
    pagination_class = PaginationCust

    @action(
        detail=False,
        permission_classes=[IsAuthenticated],
    )
    def subscriptions(self, request):
        """Просмотр подписок на авторов.Мои подписки."""
        user = request.user
        queryset = User.objects.filter(subscribe__user=user)
        pages = self.paginate_queryset(queryset)
        serializer = UserSubscriptionsSerializer(
            pages,
            many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)

    @action(
        detail=True,
        methods=['get', 'delete', 'post'],
        permission_classes=[IsAuthenticated],
    )
    def subscribe(self, request, **kwargs):
        """Подписка или отписка от автора рецептов."""
        user = request.user
        author_id = self.kwargs.get('id')
        author = get_object_or_404(User, id=author_id)

        if request.method == 'POST':
            serializer = UserSubscriptionsSerializer(
                author,
                data=request.data,
                context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            Subscriptions.objects.create(user=user, author=author)
            return Response('Подписка оформлена',
                            status=status.HTTP_204_NO_CONTENT)

        if request.method == 'DELETE':
            subscription = get_object_or_404(
                Subscriptions,
                user=user,
                author=author
            )
            subscription.delete()
            return Response('Подписка удалена',
                            status=status.HTTP_204_NO_CONTENT)


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
    permission_classes = (IsAdminAuthorOrReadOnly)
    pagination_class = PaginationCust
    # filter_backends

    def perform_create(self, serializer, **kwargs):
        serializer.save(author=self.request.user)

    def get_serializer_class(self):
        return (RecipeReadSerializer if self.request.method in SAFE_METHODS
                else RecipeRecordSerializer)

    @action(
        detail=True,
        methods=['delete', 'post'],
        permission_classes=[IsAuthenticated],
    )
    def favorite(self, request, pk):
        """Добавление или удаление рецептов в раздел Избранное."""
        if request.method == 'POST':
            return self.add_recipe(Favorite, request.user, pk)
        if request.method == 'DELETE':
            return self.delete_recipe(Favorite, request.user, pk)

    @action(
        detail=True,
        methods=['delete', 'post'],
        permission_classes=[IsAuthenticated],
    )
    def shopping_сart(self, request, pk):
        """Добавление или удаление рецептов в раздел Корзина покупок."""
        if request.method == 'POST':
            return self.add_recipe(ShoppingCart, request.user, pk)
        if request.method == 'DELETE':
            return delete_recipe(ShoppingCart, request.user, pk)

    def add_recipe(self, models, user, pk):
        """Метод добавления рецептов."""
        if models.objects.filter(user=user, recipe__id=pk).exists():
            return Response({'Ошибка': 'Рецепт уже был добавлен!'},
                            status=status.HTTP_400_BAD_REQUEST)
        recipe = get_object_or_404(Recipe, id=pk)
        models.objects.create(user=user, recipe=recipe)
        serializer = ShortRecipeSerializer(recipe)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete_recipe(self, models, user, pk):
        """Метод удаления рецепта."""
        try:
            obj = models.objects.get(user=user, recipe__id=pk)
            obj.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except models.DoesNotExist:
            return Response({'Ошибка': 'Рецепт уже был удален!'},
                            status=status.HTTP_400_BAD_REQUEST)
