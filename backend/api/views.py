from django.contrib.auth import authenticate, update_session_auth_hash
from django.shortcuts import render, get_object_or_404
from djoser.views import UserViewSet
from djoser.serializers import SetPasswordSerializer
# from rest_framework.authentication import TokenAuthentication
from rest_framework import filters, mixins, permissions, status, viewsets
from rest_framework.decorators import action 
from rest_framework.exceptions import ValidationError
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import (
    AllowAny, IsAuthenticated, IsAuthenticatedOrReadOnly)
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from .pagination import PaginationCust
from .permissions import IsAdminOrReadOnly, IsAdmitOrGetOut, IsAuthorOrReadOnly
from .serializers import (
    UserSerializer, TagSerializer, IngredientSerializer, UserSubscriptionsSerializer
)

from recipes.models import (
    Ingredient, Tag, Recipe, IngredientInRecipe, Favorite, ShoppingCart)
from users.models import User, Subscriptions


 
class CustomUserViewSet(UserViewSet):
    """Работа с пользователями. Регистрация пользователей,
     Вывод пользователей. У авторизованных пользователей возможность подписки.
     Djoser позволяет переходить по endpoints user и токена"""
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
            return Response('Подписка оформлена', status=status.HTTP_204_NO_CONTENT)

        
        if request.method == 'DELETE':
            subscription = get_object_or_404(
                Subscriptions,
                user=user,
                author=author
            )
            subscription.delete()
            return Response('Подписка удалена', status=status.HTTP_204_NO_CONTENT)
    

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
  