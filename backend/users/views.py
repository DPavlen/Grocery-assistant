from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated

from api.pagination import PaginationCust
from api.permissions import IsAdminOrReadOnly, IsAdminAuthorOrReadOnly
from rest_framework.response import Response
from users.serializers import (
    UserSerializer, UserSubscriptionsSerializer, ShortRecipeSerializer)
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
