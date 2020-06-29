from django.urls import path
from . import views

app_name = 'car_rental'

urlpatterns = [
    path('', views.MainView.as_view(), name='main'),
]
