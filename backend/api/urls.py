from django.urls import include, path
from rest_framework import routers
from rest_framework.authtoken.views import obtain_auth_token


from api.views import (CustomUserViewSet)
                    #    CurrentUserView, SetPasswordAPIView)

app_name = 'api'


router = routers.DefaultRouter()

router.register('users', CustomUserViewSet, 'users')

urlpatterns = [
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
    # path('auth/token/login/', obtain_auth_token, name='auth-token'),
    # path('api/users/me/', CurrentUserView.as_view(), name='current_user'),
    # path('', SetPasswordViewSet.as_view(), name='set_password'),
]