from django.conf.urls import url
from django.contrib import admin
from django.urls import path, include
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions
from rest_framework_jwt.views import obtain_jwt_token, refresh_jwt_token
from paypal import views as paypal_views

schema_view = get_schema_view(
   openapi.Info(
      title='CAR RENTAL API',
      default_version='v1',
      contact=openapi.Contact(email='piotr.a.mazur@wp.pl'),
      license=openapi.License(name='BSD License'),
   ),
   public=True,
   permission_classes=(permissions.AllowAny, ),
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('car_rental.urls')),
    path('api-token-auth/', obtain_jwt_token),
    path('api-token-refresh/', refresh_jwt_token, name='refresh_jwt_token'),

    path('paid',  paypal_views.PayPalSuccessView.as_view(), name='paid'),
    path('cancel', paypal_views.PayPalCancelView.as_view(), name='cancel'),

    url(
        'swagger',
        schema_view.with_ui('swagger', cache_timeout=0),
        name='schema-swagger-ui'
    ),
    url(
        'redoc',
        schema_view.with_ui('redoc', cache_timeout=0),
        name='schema-redoc'
    ),
]
