from django.urls import include, path
from rest_framework import routers
from rest_framework.authtoken.views import obtain_auth_token


from api.views import (UserViewSet)
                    #    CurrentUserView, SetPasswordAPIView)

app_name = 'api'


router = routers.DefaultRouter()

router.register('users', UserViewSet, 'users')

urlpatterns = [
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
    # path('auth/token/login/', obtain_auth_token, name='auth-token'),
    # path('api/users/me/', CurrentUserView.as_view(), name='current_user'),
    # path('auth/token/login/', SetPasswordAPIView.as_view(), name='set_password'),
]