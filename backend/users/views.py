from django_filters.rest_framework import DjangoFilterBackend
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated

from api.filters import FilterUser
from api.pagination import PaginationCust
from rest_framework.response import Response
from api.permissions import IsAdminOrReadOnly
from users.serializers import MyUserSerializer, UserSubscriptionsSerializer
from users.models import User, Subscriptions


class CustomUserViewSet(UserViewSet):
    """Работа с пользователями. Регистрация пользователей.
    Вывод пользователей. У авторизованных пользователей
    возможность подписки. Djoser позволяет переходить
    по endpoints user и токена."""

    queryset = User.objects.all()
    serializer_class = MyUserSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = FilterUser
    permission_classes = (IsAdminOrReadOnly,)
    pagination_class = PaginationCust

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def subscribe(self, request, **kwargs):
        """Подписка на автора рецептов."""

        author_id = self.kwargs.get("id")
        author = get_object_or_404(User, id=author_id)
        serializer = UserSubscriptionsSerializer(
            author, data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        Subscriptions.objects.create(user=request.user, author=author)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @subscribe.mapping.delete
    def delete_subscribe(self, request, **kwargs):
        """Отписка от автора рецептов."""

        try:
            subscription = Subscriptions.objects.get(
                user=request.user,
                author=get_object_or_404(User, id=self.kwargs.get("id")),
            )
            subscription.delete()
            return Response("Подписка удалена", status=status.HTTP_204_NO_CONTENT)
        except ObjectDoesNotExist:
            return Response(
                "Подписка не существует", status=status.HTTP_400_BAD_REQUEST
            )

    @action(
        detail=False,
        permission_classes=[IsAuthenticated],
    )
    def subscriptions(self, request):
        """Просмотр подписок на авторов.Мои подписки."""

        pages = self.paginate_queryset(
            User.objects.filter(subscribe__user=request.user)
        )
        serializer = UserSubscriptionsSerializer(
            pages, many=True, context={"request": request}
        )
        return self.get_paginated_response(serializer.data)

    @action(
        detail=False,
        methods=["get"],
        permission_classes=[IsAuthenticated],
    )
    def me(self, request):
        """Просмотр подписок на авторов.Мои подписки."""

        user = request.user
        serializer = MyUserSerializer(user, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)
