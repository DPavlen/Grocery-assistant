import io

from django.db.models import Sum
from django.db.utils import IntegrityError
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from rest_framework.exceptions import PermissionDenied
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, SAFE_METHODS
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from api.filters import FilterIngredient, FilterRecipe
from api.pagination import PaginationCust
from api.permissions import IsAuthorOrAdminOrIsAuthReadOnly
from api.serializers import (
    TagSerializer,
    IngredientSerializer,
    RecipeReadSerializer,
    RecipeRecordSerializer,
    ShortRecipeSerializer,
)

# from core
from recipes.models import (
    CompositionOfDish,
    Ingredient,
    Tag,
    Recipe,
    Favorite,
    ShoppingCart,
)


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
    permission_classes = [IsAuthorOrAdminOrIsAuthReadOnly]
    pagination_class = PaginationCust
    filter_backends = (DjangoFilterBackend,)
    filterset_class = FilterRecipe

    def get_serializer_class(self):
        """Выбор сериализатора в зависимости от действия."""

        return (
            RecipeReadSerializer
            if self.request.method in SAFE_METHODS
            else RecipeRecordSerializer
        )

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def perform_update(self, serializer):
        serializer.save(author=self.request.user)

    def partial_update(self, request, *args, **kwargs):
        """Обертка над методом update и для частичного обновления данных.
        В данном случае, параметр partial устанавливается в False,
        чтобы гарантировать, что обновление будет полным (не частичным).
        Затем метод update вызывается с переданными аргументами."""

        instance = self.get_object()
        if instance.author != request.user:
            raise PermissionDenied("Вы не можете обновить чужой рецепт")
        kwargs["partial"] = False
        return self.update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """Проверяем, является ли пользователь автором рецепта.
        И если нет, то не даем удалять чужой рецепт."""
        instance = self.get_object()
        if instance.author != request.user:
            raise PermissionDenied("Вы не можете удалить чужой рецепт")
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["post"],
            permission_classes=[IsAuthenticated])
    def favorite(self, request, pk):
        """Добавление рецептов в раздел Избранное."""

        return self.add_recipe(Favorite, request.user, pk)

    @favorite.mapping.delete
    def delete_favorite(self, request, pk):
        """Удаление рецептов из раздела Избранное."""

        return self.delete_recipe(Favorite, request.user, pk)

    @action(detail=True, methods=["post"],
            permission_classes=[IsAuthenticated])
    def shopping_cart(self, request, pk):
        """Добавление рецептов в раздел Корзина покупок."""

        return self.add_recipe(ShoppingCart, request.user, pk)

    @shopping_cart.mapping.delete
    def delete_shopping_сart(self, request, pk):
        """Удаление рецептов в раздел Корзина покупок."""

        return self.delete_recipe(ShoppingCart, request.user, pk)

    def add_recipe(self, models, user, pk):
        """Метод добавления рецептов. Различные проверки."""

        if not Recipe.objects.filter(id=pk).exists():
            return Response(
                {"Ошибка": "Такого рецепта не существует!"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            recipe = get_object_or_404(Recipe, id=pk)
            if models.objects.filter(user=user,
                                     recipe=recipe).exists():
                return Response(
                    {"Ошибка": "Рецепт уже добавлен!"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            models.objects.create(user=user, recipe=recipe)
            serializer = ShortRecipeSerializer(recipe)
            return Response(serializer.data,
                            status=status.HTTP_201_CREATED)
        except IntegrityError:
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={"detail": "Рецепт уже добавлен!"},
            )

    def delete_recipe(self, models, user, pk):
        """Метод удаления рецепта."""

        try:
            obj = get_object_or_404(
                models, user=user,
                recipe__id=pk)
            obj.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except models.DoesNotExist:
            return Response(
                status=status.HTTP_404_NOT_FOUND,
                data={"detail": "Not found."}
            )

    @action(detail=False, methods=["get"],
            permission_classes=[IsAuthenticated])
    def download_shopping_cart(self, request):
        """Получение списка покупок у текущего пользователя из
        базы данных. Использует этот буфер для создания
        HTTP-ответа с прикрепленным PDF-файлом."""

        pdf_filename = "shopping_cart.pdf"
        buffer = io.BytesIO()
        pdfmetrics.registerFont(TTFont("DejaVuSans", "DejaVuSans.ttf"))

        pdf = canvas.Canvas(buffer)
        y = 800
        recipes = Recipe.objects.filter(shoppingcart__user=request.user)
        buy_list = (
            CompositionOfDish.objects.filter(recipe__in=recipes)
            .values("ingredient__name", "ingredient__measurement_unit")
            .annotate(total_amount=Sum("amount"))
            .order_by("ingredient__name")
        )
        buy_list_text = "Foodgram - Список покупок: \n"
        for item in buy_list.values(
            "ingredient__name",
            "ingredient__measurement_unit",
            "total_amount",
        ):
            amount = item["total_amount"]
            name = item["ingredient__name"]
            measurement_unit = item["ingredient__measurement_unit"]
            buy_list_text += f"{name}, {amount} {measurement_unit} \n"

        pdf.setFont("DejaVuSans", 14)
        print(buy_list_text)
        lines = buy_list_text.split("\n")
        for line in lines:
            line = line.strip()
            pdf.drawString(100, y, line)
            y -= 20

        y -= 20
        pdf.showPage()
        pdf.save()
        buffer.seek(0)
        response = HttpResponse(buffer.getvalue(),
                                content_type="application/pdf")
        response["Content-Disposition"] = (
            f'attachment; filename="'
            f'{pdf_filename}"'
        )
        return response
