from django.urls import path

from . import views

app_name = 'car_rental'

urlpatterns = [
    path('', views.MainView.as_view(), name='main'),
    path('signup', views.SignUp.as_view(), name='sign_up'),
    path('client/<int:pk>', views.ClientDataAPI.as_view(),
         name='client_pk'),
    path('client/single/<str:username>', views.ClientDataAPI.as_view(),
         name='client'),
    path('cars', views.CarsAPI.as_view(), name='cars'),
    path('cars/<int:pk>', views.CarsAPI.as_view(), name='cars'),
    path('segments', views.SegmentsAPI.as_view(), name='segments'),
    path('segments/<int:pk>', views.SegmentsAPI.as_view(),
         name='segments_pk'),
    path('segment/<int:id>', views.SingleSegmentAPI.as_view(), name='segment'),
    path('checkres', views.CheckReservationAPI.as_view(), name='check_res'),
    path('terms/<int:car_id>', views.TermsAPI.as_view(), name='terms'),
    path('reservation/<int:pk>', views.ReservationAPI.as_view(),
         name='reservation'),
    path('reservation', views.ClientReservationAPI.as_view(),
         name='client_reservation'),
    path('clients', views.ClientsAPI.as_view(), name='clients'),
    path('discounts', views.DiscountsAPI.as_view(), name='discounts'),
    path('discounts/<int:pk>', views.DiscountsAPI.as_view(),
         name='discounts_pk'),
    path('order', views.OrderAPI.as_view(), name='new_order'),
    path('order/<int:pk>', views.OrderAPI.as_view(), name='existing_order'),
]
