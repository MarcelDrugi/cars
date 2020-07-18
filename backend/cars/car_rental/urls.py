from django.urls import path
from . import views


app_name = 'car_rental'

urlpatterns = [
    path('', views.MainView.as_view(), name='main'),
    path('signup', views.SignUp.as_view(), name='sign_up'),
    path('test', views.Test.as_view(), name='test'),
    path('cars', views.CarsAPI.as_view(), name='cars'),
    path('delcar/<int:pk>', views.DeleteCarAPI.as_view(), name='del_car'),
    path('segments', views.SegmentsAPI.as_view(), name='segments'),
    path(
        'putdelsegment/<int:pk>',
        views.PutDeleteSegmentAPI.as_view(),
        name='del_segment'
    ),
]
