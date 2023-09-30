from django.shortcuts import render, get_object_or_404
from rest_framework import filters, mixins, permissions, status, viewsets
from rest_framework.decorators import action 
from rest_framework.exceptions import ValidationError
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import (
    AllowAny, IsAuthenticated, IsAuthenticatedOrReadOnly)
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet


from .permissions import IsAdminOrReadOnly, IsAdmitOrGetOut, IsAuthorOrReadOnly
from .serializers import (
    UserSerializer,
)

from recipes.models import (
    Ingredient, Tag, Recipe, IngredientInRecipe, Favorite, ShoppingCart)
from users.models import User, Subscription




class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    http_method_names = ['get', 'post', 'patch', 'delete']
    permission_classes = (IsAdminOrReadOnly,)

    def perform_create(self, serializer):
        if self.request.user.role == 'admin':
            if not self.request.POST.get('email'):
                raise ValidationError('запись уже существует.')
        serializer.save()

    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'create']:
            return (IsAdmitOrGetOut(),)
        return super().get_permissions()

    @action(
        methods=['GET', 'PATCH'],
        detail=False,
        # url_path='me',
        permission_classes=[permissions.IsAuthenticated],
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
