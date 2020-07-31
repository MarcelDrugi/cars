from django.urls import path
from . import views


app_name = 'car_rental'

urlpatterns = [
    path('', views.MainView.as_view(), name='main'),
    path('signup', views.SignUp.as_view(), name='sign_up'),
    path('avatar/<str:username>', views.AvatarAPI.as_view(), name='avatar'),
    path('cars', views.CarsAPI.as_view(), name='cars'),
    path('cars/<int:pk>', views.CarsAPI.as_view(), name='cars'),
    path('segments', views.SegmentsAPI.as_view(), name='segments'),
    path('segments/<int:pk>', views.SegmentsAPI.as_view(),
         name='segments'),
    path('segment/<int:id>', views.SingleSegmentAPI.as_view(), name='segment'),
    path('checkres', views.CheckReservationAPI.as_view(), name='check_res'),
    path('reservation/<int:pk>', views.ReservationAPI.as_view(),
         name='reservation'),
    path('clients', views.ClientsAPI.as_view(), name='clients'),
    path('discounts', views.DiscountsAPI.as_view(), name='discounts'),
    path('discounts/<int:pk>', views.DiscountsAPI.as_view(), name='discounts'),
    path('order', views.Order.as_view(), name='order'),
]
