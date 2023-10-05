from django.shortcuts import get_object_or_404
from requests import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
from rest_framework import status

from .serializers import ShortRecipeSerializer
from recipes.models import Recipe


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
    