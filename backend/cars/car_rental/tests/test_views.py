import datetime
import json
from datetime import date
from unittest.mock import Mock
from django.contrib.auth.models import User, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from django.test import Client, TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.exceptions import ErrorDetail
from rest_framework.test import APITestCase
from car_rental import views
from car_rental.managers import ClientManager
from car_rental.models import Clients, Discounts, Cars, PriceLists, Segments, \
    Reservations, Orders
from car_rental.permissions import RightsSupport
from car_rental.tests.shared import TestWithCar


class AuthorizedAPITestCase(APITestCase):
    def get_token(self, user_data):
        login_response = self.client.post(
            '/api-token-auth/',
            data=json.dumps(user_data),
            content_type='application/json'
        )
        return 'JWT ' + login_response.data['token']


class SignUpTestCase(APITestCase):
    """
    Test of API-view used for user registration.
    """
    # correct request
    def test_correct_request(self):
        reg_data = {
            'first_name': 'Jan',
            'last_name': 'Kowalski',
            'email': 'jan@kowalski.pl',
            'username': 'some_username',
            'password': 'some_password',
            'avatar': 'undefined'
        }

        response = self.client.post(reverse('car_rental:sign_up'), reg_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            response.data['user']['first_name'],
            reg_data['first_name']
        )
        self.assertEqual(
            response.data['user']['last_name'],
            reg_data['last_name']
        )
        self.assertEqual(
            response.data['user']['username'],
            reg_data['username']
        )
        self.assertEqual(response.data['user']['email'], reg_data['email'])

    # incorrect request
    def test_incorrect_request(self):
        reg_data = {
            'first_name': 'Jan',
            'last_name': 'Kowalski',
            'email': 'jan@kowalski,pl',  # invalid email format
            'username': 'some_username',
            'password': 'some_password',
            'avatar': 'undefined'
        }

        response = self.client.post(reverse('car_rental:sign_up'), reg_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data['user']['email'][0],
            ErrorDetail(string='Enter a valid email address.', code='invalid')
        )


class ClientDataAPITestCase(AuthorizedAPITestCase):
    def setUp(self):
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

    def test_get_client(self):
        """ GET Client and avatar by username """
        token = self.get_token(self.user_data)

        response = self.client.get(
            reverse('car_rental:client', kwargs={
                'username': self.user_data['username']
            }),
            HTTP_AUTHORIZATION=token,
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        empty_avatar_name = ClientManager.EMPTY_AVATAR
        name_in_response = response.data['avatar']['avatar'].split('/')[-1]
        self.assertEqual(empty_avatar_name, name_in_response)
        self.assertEqual(
            response.data['client']['user']['username'],
            self.user_data['username']
        )

    def test_patch_client(self):
        initial_client = Clients.objects.last()
        token = self.get_token(self.user_data)

        # patch user's data:
        data_to_patch = self.user_data.copy()
        data_to_patch['username'] = 'Other username'

        response = self.client.patch(
            reverse('car_rental:client_pk', kwargs={
                'pk': initial_client.id
            }),
            data_to_patch,
            HTTP_AUTHORIZATION=token,
        )
        patched_client = get_object_or_404(Clients, id=initial_client.id)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotEqual(
            initial_client.user.username, self.user_data['username']
        )
        self.assertIn('token', response.data)
        self.assertEqual(
            initial_client.user.username, data_to_patch['username']
        )

    def test_patch_password(self):
        pass_to_patch = {
            'old_password': self.user_data['password'],
            'new_password': 'some_new_pass'
        }
        initial_client = Clients.objects.last()

        token = self.get_token(self.user_data)
        response = self.client.patch(
            reverse('car_rental:client_pk', kwargs={
                'pk': initial_client.id
            }),
            pass_to_patch,
            HTTP_AUTHORIZATION=token,
        )
        patched_client = get_object_or_404(Clients, id=initial_client.id)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(
            patched_client.user.check_password(pass_to_patch['new_password'])
        )
        self.assertIn('token', response.data)


class ClientsAPITestCase(AuthorizedAPITestCase):
    def setUp(self):
        self.workers_data = {
            'username': 'some_username',
            'password': 'some_pass'
        }
        User.objects.create_user(**self.workers_data)
        user = User.objects.create_user(
            username='username_1',
            password='some_pass'
        )
        Clients.objects.create_client(user=user, avatar=None)

    def test_get_clients(self):
        token = self.get_token(self.workers_data)

        response = self.client.get(
            reverse('car_rental:clients'),
            HTTP_AUTHORIZATION=token,
        )
        clients = Clients.objects.all()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(clients.count(), 1)
        self.assertTrue(clients.last().user.has_perm('car_rental.client'))


class DiscountsAPITestCase(AuthorizedAPITestCase):
    def setUp(self):
        self.workers_data = {
            'username': 'some_username',
            'password': 'some_pass'
        }
        user = User.objects.create_user(**self.workers_data)
        content_type = ContentType.objects.get_for_model(RightsSupport)
        client_perm = Permission.objects.get(
            content_type=content_type,
            codename='employee'
        )
        user.user_permissions.add(client_perm)

        self.discount = Discounts.objects.create(
            discount_code=35792468,
            discount_value=0.4
        )
        clients_user = User.objects.create_user(
            username='clients_username',
            password='some_pass'
        )
        self.client_ = Clients.objects.create_client(
            user=clients_user,
            avatar=None
        )

    def test_post_discount(self):
        new_discount_data = {
            'discount_code': 555917,
            'discount_value': 0.1
        }
        token = self.get_token(self.workers_data)

        response = self.client.post(
            reverse('car_rental:discounts'),
            new_discount_data,
            HTTP_AUTHORIZATION=token,
        )
        added_discount = Discounts.objects.last()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Discounts.objects.all().count(), 2)
        self.assertEqual(
            added_discount.discount_code,
            new_discount_data['discount_code']
        )
        self.assertEqual(
            added_discount.discount_value,
            new_discount_data['discount_value']
        )
        self.assertIn('token', response.data)

    def test_get_discount(self):
        token = self.get_token(self.workers_data)
        response = self.client.get(
            reverse('car_rental:discounts'),
            HTTP_AUTHORIZATION=token,
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data[1])
        self.assertEqual(Discounts.objects.all().count(), 1)

    def test_add_discount_to_client(self):
        token = self.get_token(self.workers_data)
        data = {
            'client': self.client_.user.username,
            'discount': self.discount.id,
            'acction': 'add',
        }
        response = self.client.put(
            reverse('car_rental:discounts'),
            data,
            HTTP_AUTHORIZATION=token,
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)
        self.assertGreater(self.client_.discount.all().count(), 0)
        self.assertEqual(
            self.client_.discount.last().discount_code,
            self.discount.discount_code
        )

    def test_separate_discount_from_the_client(self):
        # adding a discount to the client
        self.client_.discount.add(self.discount)

        token = self.get_token(self.workers_data)
        data = {
            'client': self.client_.user.username,
            'discount': self.discount.id,
            'acction': 'remove',
        }
        response = self.client.put(
            reverse('car_rental:discounts'),
            data,
            HTTP_AUTHORIZATION=token,
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)
        self.assertEqual(self.client_.discount.all().count(), 0)

    def test_delete_discount(self):
        token = self.get_token(self.workers_data)
        response = self.client.delete(
            reverse(
                'car_rental:discounts_pk',
                kwargs={'pk': self.discount.id}
            ),
            HTTP_AUTHORIZATION=token,
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)
        self.assertEqual(Discounts.objects.all().count(), 0)


class CarsAPITestCase(AuthorizedAPITestCase, TestWithCar):
    """
    A class that tests view that support the Cars model.
    CarsAPI (name=cars) -> GET, POST, PUT
    """
    def setUp(self):
        super(CarsAPITestCase, self).setUp()
        # client-user -> necessary to receive a token
        self.user_data = {'username': 'Username', 'password': 'some_pass'}
        user = User.objects.create_user(**self.user_data)
        content_type = ContentType.objects.get_for_model(RightsSupport)
        client_perm = Permission.objects.get(
            content_type=content_type,
            codename='employee'
        )
        user.user_permissions.add(client_perm)

    def test_get(self):
        response = self.client.get(reverse('car_rental:cars'))

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(response.data[0]['brand'], self.car_data['brand'])
        self.assertEqual(response.data[0]['model'], self.car_data['model'])
        self.assertEqual(
            response.data[0]['reg_number'],
            self.car_data['reg_number']
        )
        self.assertEqual(
            response.data[0]['description'],
            self.car_data['description']
        )
        self.assertEqual(
            response.data[0]['segment']['name'],
            self.car_data['segment'].name
        )
        self.assertEqual(
            response.data[0]['segment']['pricing']['hour'],
            self.car_data['segment'].pricing.hour
        )
        self.assertEqual(
            response.data[0]['segment']['pricing']['week'],
            self.car_data['segment'].pricing.week
        )

        self.assertEqual(response.data[1]['token'], None)

    def test_correct_post(self):
        # copy car data
        new_car_data = self.car_data

        # change fields to create dict for request
        new_car_data['id'] += 1
        new_car_data['segment'] = self.segment_id
        new_car_data['reg_number'] += 'x'

        token = self.get_token(self.user_data)

        response = self.client.post(
            reverse('car_rental:cars'),
            new_car_data,
            HTTP_AUTHORIZATION=token,
        )
        cars = Cars.objects.all()

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(cars), 2)
        self.assertIn('token', response.data)

    def test_incorrect_post(self):
        # copy car data
        new_car_data = self.car_data

        # change fields to create dict for incorrect request
        new_car_data['id'] += 1
        new_car_data['segment'] = self.segment_id
        new_car_data['reg_number'] += 'xxxxx'  # too long reg number

        token = self.get_token(self.user_data)

        response = self.client.post(
            reverse('car_rental:cars'),
            new_car_data,
            HTTP_AUTHORIZATION=token,
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('token', response.data)  # refresh token even when 400

    def test_correct_put(self):
        updated_car_data = self.car_data
        updated_car_data['brand'] = 'other brand'  # change brand
        updated_car_data['segment'] = self.segment_id

        token = self.get_token(self.user_data)

        response = self.client.put(
            reverse('car_rental:cars'),
            updated_car_data,
            HTTP_AUTHORIZATION=token,
        )
        cars = Cars.objects.all()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(cars[0].brand, updated_car_data['brand'])
        self.assertIn('token', response.data)

    def test_incorrect_put(self):
        updated_car_data = self.car_data
        updated_car_data['reg_number'] = 'to_long_reg_number'  # change brand
        updated_car_data['segment'] = self.segment_id

        token = self.get_token(self.user_data)

        response = self.client.put(
            reverse('car_rental:cars'),
            updated_car_data,
            HTTP_AUTHORIZATION=token
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('token', response.data)  # refresh token even when 400

    def test_del_car(self):
        token = self.get_token(self.user_data)

        url = reverse('car_rental:cars', kwargs={'pk': self.car_data['id']})
        response = self.client.delete(url, HTTP_AUTHORIZATION=token)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(Cars.objects.all()), 0)
        self.assertIn('token', response.data)


class SegmentsAPITestCase(AuthorizedAPITestCase):
    def setUp(self):
        # pricing
        self.pricing_data = {
            'id': 22,
            'hour': 29.50,
            'day': 95.00,
            'week': 449.99
        }
        self.pricing = PriceLists.objects.create(**self.pricing_data)

        # segment
        self.segment_data = {
            'id': 57,
            'name': 'example_name',
            'pricing': self.pricing
        }
        self.segment = Segments.objects.create(**self.segment_data)

        # client-user (necessary to receive a token)
        self.user_data = {'username': 'Username', 'password': 'some_pass'}
        user = User.objects.create_user(**self.user_data)
        content_type = ContentType.objects.get_for_model(RightsSupport)
        client_perm = Permission.objects.get(
            content_type=content_type,
            codename='employee'
        )
        user.user_permissions.add(client_perm)

    def test_get(self):
        response = self.client.get(reverse('car_rental:segments'))

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(response.data[0]['name'], self.segment_data['name'])
        self.assertEqual(
            response.data[0]['pricing']['hour'],
            self.segment_data['pricing'].hour
        )
        self.assertEqual(
            response.data[0]['pricing']['day'],
            self.segment_data['pricing'].day
        )
        self.assertEqual(
            response.data[0]['pricing']['week'],
            self.segment_data['pricing'].week
        )

    def test_correct_post(self):
        # copy segment data
        new_segment_data = self.segment_data

        # change fields to create dict for request
        new_segment_data['id'] += 1
        new_segment_data['pricing'] = self.pricing_data

        token = self.get_token(self.user_data)

        response = self.client.post(
            reverse('car_rental:segments'),
            data=json.dumps(new_segment_data),
            content_type='application/json',
            HTTP_AUTHORIZATION=token,
        )
        segments = Segments.objects.all()

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(segments), 2)
        self.assertIn('token', response.data)

    def test_unauthorized_post(self):
        response = self.client.post(
            reverse('car_rental:segments'),
            data=json.dumps({}),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_incorrect_post(self):
        # copy segment data
        new_segment_data = self.segment_data

        # change fields to create dict for request
        new_segment_data['id'] += 1
        new_segment_data['pricing'] = self.pricing_data
        new_segment_data['pricing']['hour'] = 'text'  # wrong type

        token = self.get_token(self.user_data)

        response = self.client.post(
            reverse('car_rental:segments'),
            data=json.dumps(new_segment_data),
            content_type='application/json',
            HTTP_AUTHORIZATION=token,
        )
        segments = Segments.objects.all()

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(len(segments), 1)
        self.assertIn('token', response.data)

    def test_correct_put(self):
        updated_segment_data = self.segment_data
        updated_segment_data['pricing'] = self.pricing_data
        updated_segment_data['name'] = 'other name'  # change the name

        token = self.get_token(self.user_data)

        response = self.client.put(
            reverse(
                'car_rental:segments_pk',
                kwargs={'pk': self.segment_data['id']}
            ),
            data=json.dumps(updated_segment_data),
            content_type='application/json',
            HTTP_AUTHORIZATION=token,
        )
        segments = Segments.objects.all()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(segments.count(), 1)  # still 1 object
        self.assertEqual(response.data['name'], updated_segment_data['name'])
        self.assertIn('token', response.data)

    def test_incorrect_put(self):
        updated_segment_data = self.segment_data
        updated_segment_data['pricing'] = self.pricing_data
        updated_segment_data['pricing']['week'] = 'text'  # wrong format

        token = self.get_token(self.user_data)

        response = self.client.put(
            reverse(
                'car_rental:segments_pk',
                kwargs={'pk': self.segment_data['id']}
            ),
            data=json.dumps(updated_segment_data),
            content_type='application/json',
            HTTP_AUTHORIZATION=token,
        )
        segments = Segments.objects.all()

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # name unchanged
        self.assertEqual(segments[0].name, self.segment_data['name'])

    def test_del_segment(self):
        token = self.get_token(self.user_data)

        url = reverse(
            'car_rental:segments_pk',
            kwargs={'pk': self.segment_data['id']}
        )
        response = self.client.delete(url, HTTP_AUTHORIZATION=token)

        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        self.assertEqual(Segments.objects.all().count(), 0)
        self.assertIn('token', response.data)


class SingleSegmentAPITestCase(APITestCase):
    def setUp(self):
        self.pricing_data = {
            'id': 4,
            'hour': 29.50,
            'day': 145.99,
            'week': 480.00
        }
        self.pricing = PriceLists.objects.create(**self.pricing_data)
        self.segment_id = 1
        Segments.objects.create(
            id=self.segment_id,
            name='name',
            pricing=self.pricing
        )

    def test_get_single_segment(self):
        response = self.client.get(
            reverse('car_rental:segment', kwargs={'id': self.segment_id})
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)
        self.assertEqual(
            response.data['segment']['pricing'],
            self.pricing_data
        )
        self.assertEqual(response.data['segment']['id'], self.segment_id)


class CheckReservationAPITestCase(AuthorizedAPITestCase, TestWithCar):
    def setUp(self):
        super(CheckReservationAPITestCase, self).setUp()

        # client-user -> necessary to receive a token
        self.user_data = {'username': 'tester', 'password': 'secret_pass'}
        user = User.objects.create_user(**self.user_data)
        Clients.objects.create_client(user=user, avatar=None)

        # creating reservation with a car, inherited from TestWithCar class
        self.reservation_data = {
            'car': self.car,
            'begin': date.today() + datetime.timedelta(days=5),
            'end': date.today() + datetime.timedelta(days=12),
        }
        Reservations.objects.create(**self.reservation_data)

    def test_free_reservation_term(self):
        begin_date = (self.reservation_data['end'] +
                      datetime.timedelta(days=1)).strftime('%d.%m.%Y')
        end_date = (self.reservation_data['end'] +
                    datetime.timedelta(days=3)).strftime('%d.%m.%Y')
        checking_reservation_data = {
            'begin': begin_date,
            'end': end_date,
            'segment': self.car.segment.id
        }

        token = self.get_token(self.user_data)
        response = self.client.post(
            reverse('car_rental:check_res', ),
            data=checking_reservation_data,
            HTTP_AUTHORIZATION=token,
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            response.data['client']['user']['username'],
            self.user_data['username']
        )
        self.assertEqual(
            response.data['reservation']['car']['id'],
            self.car.id
        )
        self.assertIn('token', response.data)

    def test_not_available_reservation_term(self):
        checking_reservation_data = {
            'begin': self.reservation_data['end'].strftime('%d.%m.%Y'),
            'end': self.reservation_data['end'].strftime('%d.%m.%Y'),
            'segment': self.car.segment.id
        }

        token = self.get_token(self.user_data)
        try:
            self.client.post(
                reverse('car_rental:check_res', ),
                data=checking_reservation_data,
                HTTP_AUTHORIZATION=token,
            )
        except ValidationError as exception:
            self.assertEqual(len(exception.messages), 1)
            self.assertEqual(exception.messages[0], 'Term is not free.')


class ReservationAPITestCase(AuthorizedAPITestCase, TestWithCar):
    def setUp(self):
        super(ReservationAPITestCase, self).setUp()

        # client-user -> necessary to receive a token
        self.user_data = {'username': 'tester', 'password': 'secret_pass'}
        user = User.objects.create_user(**self.user_data)
        Clients.objects.create_client(user=user, avatar=None)

        # creating reservation with a car, inherited from TestWithCar class
        self.reservation_data = {
            'car': self.car,
            'begin': date.today() + datetime.timedelta(days=5),
            'end': date.today() + datetime.timedelta(days=12),
        }
        Reservations.objects.create(**self.reservation_data)

    def test_get_reservation(self):
        reservation = Reservations.objects.last()
        token = self.get_token(self.user_data)
        response = self.client.get(
            reverse('car_rental:reservation', kwargs={'pk': reservation.id}),
            HTTP_AUTHORIZATION=token,
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)
        self.assertEqual(reservation.id, response.data['reservation']['id'])

    def test_delete_reservation(self):
        reservation = Reservations.objects.last()
        token = self.get_token(self.user_data)
        response = self.client.delete(
            reverse('car_rental:reservation', kwargs={'pk': reservation.id}),
            HTTP_AUTHORIZATION=token,
        )
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        self.assertIn('token', response.data)
        self.assertEqual(Reservations.objects.count(), 0)


class ClientReservationAPITestCase(AuthorizedAPITestCase, TestWithCar):
    def setUp(self):
        super(ClientReservationAPITestCase, self).setUp()
        self.user_data = {'username': 'tester', 'password': 'secret_pass'}
        self.user = User.objects.create_user(**self.user_data)
        client = Clients.objects.create_client(user=self.user, avatar=None)

        self.order = Orders.objects.create(
            client=client,
            cost=250.00,
            paid=False,
            payment_id='12x5de3r342',
        )

        self.reservation_data = {
            'car': self.car,
            'begin': date.today() + datetime.timedelta(days=5),
            'end': date.today() + datetime.timedelta(days=12),
            'order': self.order
        }
        self.reservation = Reservations.objects.create(**self.reservation_data)

    def test_get_clients_reservation(self):
        self.client.login(**self.user_data)
        token = self.get_token(self.user_data)

        response = self.client.get(
            reverse('car_rental:client_reservation', ),
            HTTP_AUTHORIZATION=token,
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]['id'], self.reservation.id)
        self.assertEqual(response.data[0]['car']['id'], self.car.id)
        self.assertEqual(response.data[0]['order']['cost'], self.order.cost)
        self.assertIn('token', response.data[-1])


class TermsAPITestCase(APITestCase, TestWithCar):
    def setUp(self):
        super(TermsAPITestCase, self).setUp()
        self.reservation_data = {
            'car': self.car,
            'begin': date.today(),
            'end': date.today() + datetime.timedelta(days=3),
        }
        Reservations.objects.create(**self.reservation_data)

    def test_reservations_list(self):
        response = self.client.get(
            reverse('car_rental:terms', kwargs={'car_id': self.car.id}),
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Reservations.objects.count(), 1)
        reservation = Reservations.objects.last()
        self.assertEqual(reservation.begin, self.reservation_data['begin'])
        self.assertEqual(reservation.end, self.reservation_data['end'])
        self.assertEqual(reservation.car, self.car)


class OrderAPITestCase(AuthorizedAPITestCase, TestWithCar):
    def setUp(self):
        super(OrderAPITestCase, self).setUp()
        self.user_data = {'username': 'tester', 'password': 'secret_pass'}
        user = User.objects.create_user(**self.user_data)
        self.client_ = Clients.objects.create_client(user=user, avatar=None)

        self.paypal_response = {
            'id': 'as23fs3ds35',
            'links': [{}, {'href': 'my_link'}],
        }

        self.major_data = {
            'reserved_car': self.car.id,
            'begin': date.today(),
            'end': date.today() + datetime.timedelta(days=5),
            'client': self.user_data['username'],
            'cost': 310.50,
            'comments': 'some_comment'
        }

    def test_correct_post_new_order(self):
        token = self.get_token(self.user_data)
        views.OrderAPI._get_payment_link = Mock(
            return_value=self.paypal_response
        )
        response = self.client.post(
            reverse('car_rental:new_order', ),
            self.major_data,
            HTTP_AUTHORIZATION=token,
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data['payment_link'],
            self.paypal_response['links'][1]['href']
        )

    def test_incorrect_post_new_order(self):
        self.major_data['reserved_car'] = self.car.id + 1
        token = self.get_token(self.user_data)
        response = self.client.post(
            reverse('car_rental:new_order', ),
            self.major_data,
            HTTP_AUTHORIZATION=token,
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_pay_existing_reservation(self):
        order = Orders.objects.create(
            client=self.client_,
            cost=120.00,
            paid=False,
            payment_id='g42xas3df72ao',
        )
        reservation_data = {
            'car': self.car,
            'begin': date.today(),
            'end': date.today() + datetime.timedelta(days=1),
            'order': order
        }
        reservation = Reservations.objects.create(**reservation_data)

        token = self.get_token(self.user_data)
        response = self.client.get(
            reverse('car_rental:existing_order', kwargs={'pk': reservation.id}),
            HTTP_AUTHORIZATION=token,
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data['payment_link'],
            self.paypal_response['links'][1]['href']
        )


class MainTestCase(TestCase):
    """
    Test of the basic view loading Angular static files.
    """
    def test_main_view(self):
        response = Client().get(reverse('car_rental:main'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTemplateUsed(response, 'car_rental/index.html')
