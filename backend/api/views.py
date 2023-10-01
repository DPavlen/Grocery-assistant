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
    UserSerializer, TagSerializer, IngredientSerializer
)

from recipes.models import (
    Ingredient, Tag, Recipe, IngredientInRecipe, Favorite, ShoppingCart)
from users.models import User, Subscription


 


class CustomUserViewSet(UserViewSet):
    """Работа с пользователями. Регистрация пользователей,
     Вывод пользователей. У авторизованных пользователей возможность подписки.
     Djoser позволяет переходить по endpoints user и токена"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAdminOrReadOnly,)
    pagination_class = PaginationCust
    link_model = Subscription
    @action(
        detail=True,
        methods=['get', 'delete', 'patch'],
        permission_classes=[IsAuthenticated],
    )
    def get_patch_me(self, request):
        user = get_object_or_404(User, username=self.request.user)
        if request.method == 'GET':
            serializer = UserSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        if request.method == 'PATCH':
            serializer = UserSerializer(
                user, data=request.data, partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)



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
  