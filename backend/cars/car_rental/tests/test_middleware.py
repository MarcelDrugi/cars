import datetime
from datetime import date

from django.contrib.auth.models import User
from django.urls import reverse

from .shared import TestWithCar
from .test_views import AuthorizedAPITestCase
from ..models import Clients, Reservations, Requests


class TrafficMiddlewareTestCase(AuthorizedAPITestCase, TestWithCar):
    """
    Request writer middleware test. Middleware should create objects with
    different fields for authorized and unauthorized requests.
    """
    def setUp(self):
        super(TrafficMiddlewareTestCase, self).setUp()
        # client-user (necessary to receive a token)
        self.user_data = {
            'username': 'Username',
            'first_name': 'First',
            'last_name': 'Last',
            'email': 'some@email.com',
            'password': 'some_pass'
        }
        user = User.objects.create_user(**self.user_data)
        Clients.objects.create_client(user=user, avatar=None)

        # creating reservation with a car, inherited from TestWithCar class
        self.reservation_data = {
            'car': self.car,
            'begin': date.today() + datetime.timedelta(days=5),
            'end': date.today() + datetime.timedelta(days=12),
        }

    def test_unauthorized(self):
        self.client.get(reverse('car_rental:cars'))
        requests = Requests.objects.all()
        self.assertEqual(requests.count(), 1)
        self.assertEqual(requests.last().authorisation, False)

    def test_authorized(self):
        Reservations.objects.create(**self.reservation_data)
        reservation = Reservations.objects.last()
        token = self.get_token(self.user_data)
        # Testing on get-Reservation endpoint
        self.client.get(
            reverse('car_rental:reservation', kwargs={'pk': reservation.id}),
            HTTP_AUTHORIZATION=token,
        )
        requests = Requests.objects.all()
        self.assertEqual(requests.count(), 2)
        self.assertEqual(requests.last().authorisation, True)
