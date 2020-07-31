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
   public=False,
   permission_classes=(permissions.AllowAny, ),
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('car_rental.urls')),
    path(r'api-token-auth/', obtain_jwt_token),
    path(r'api-token-refresh/', refresh_jwt_token, name='refresh_jwt_token'),

    path('success',  paypal_views.PayPalSuccessView.as_view(), name='success'),
    path('cancel', paypal_views.PayPalCancelView.as_view(), name='cancel'),

    url(
        r'^swagger(?P<format>\.json|\.yaml)$',
        schema_view.without_ui(cache_timeout=0),
        name='schema-json'
    ),
]
