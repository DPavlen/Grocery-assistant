from django.urls import include, path
from rest_framework import routers

from api.views import (UserViewSet)

app_name = 'api'


router = routers.DefaultRouter()

router.register('users', UserViewSet, 'users')

urlpatterns = [
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]