from django.urls import include, path
from rest_framework import routers

from api.views import (CustomUserViewSet, TagViewSet, IngredientViewSet)
             

app_name = 'api'


router = routers.DefaultRouter()

router.register('users', CustomUserViewSet, 'users')
router.register('tags', TagViewSet, 'tags')
router.register('ingredients', IngredientViewSet, 'ingredients')


urlpatterns = [
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]