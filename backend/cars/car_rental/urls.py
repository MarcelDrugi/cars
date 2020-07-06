from django.urls import path
from .middleware import RefreshTokenMiddleware
from django.utils.decorators import decorator_from_middleware_with_args
from rest_framework_jwt.views import obtain_jwt_token, refresh_jwt_token
from . import views


app_name = 'car_rental'

urlpatterns = [
    path('', views.MainView.as_view(), name='main'),
    path('signup', views.SignUp.as_view(), name='sign_up'),
    path('test', views.Test.as_view(), name='test'),
    path(r'api-token-auth/', obtain_jwt_token),
    path(r'api-token-refresh/', refresh_jwt_token),
]
