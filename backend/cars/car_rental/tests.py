"""
Unit tests.
File divided into 5 parts: API-Views, Views, URLs, Models and Managers tests.

Although it's hard to call API-views tests as a unit tests, because their
functionality is closely related to manually created serializers, but they
help to control the application operation.
"""
from datetime import date
import django
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.exceptions import ValidationError
from django.test import TestCase, Client
from django.urls import reverse, resolve
import json
from rest_framework.exceptions import ErrorDetail
from rest_framework.test import APITestCase
from .models import *
from .serializers import UserSerializer


class TestWithCar(TestCase):
    def setUp(self):
        # pricing
        self.pricing_data = {
            'id': 2,
            'hour': 15.50,
            'day': 85.99,
            'week': 320.50
        }
        self.pricing = PriceLists.objects.create(**self.pricing_data)

        # segment
        self.segment_id = 5
        self.name = 'example_name'
        self.segment = Segments.objects.create(
            id=self.segment_id,
            name=self.name,
            pricing=self.pricing
        )

        # cars
        self.car_data = {
            'id': 33,
            'brand': 'some brand',
            'model': 'some model',
            'reg_number': 'abcd123',
            'segment': self.segment,
            'description': 'description of the example car',
        }
        self.car = Cars.objects.create(**self.car_data)


# API-VIEWS

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
        self.assertEqual(response.status_code, 201)
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
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.data['user']['email'][0],
            ErrorDetail(string='Enter a valid email address.', code='invalid')
        )


class ClientDataAPITestCase(AuthorizedAPITestCase):
    def setUp(self):
        super(ClientDataAPITestCase, self).setUp()
        # client-user (necessary to receive a token)
        self.user_data = {'username': 'Username', 'password': 'some_pass'}
        user = User.objects.create_user(**self.user_data)
        Clients.objects.create_client(user=user, avatar=None)

    def test_get_client(self):
        """ GET Client and avatar by username """
        # get token:
        token = self.get_token(self.user_data)

        response = self.client.get(
            reverse('car_rental:client', kwargs={
                'username': self.user_data['username']
            }),
            HTTP_AUTHORIZATION=token,
        )
        self.assertEqual(response.status_code, 200)

        empty_avatar_name = ClientManager.EMPTY_AVATAR
        name_in_response = response.data['avatar']['avatar'].split('/')[-1]
        self.assertEqual(empty_avatar_name, name_in_response)
        self.assertEqual(
            response.data['client']['user']['username'],
            self.user_data['username']
        )

    def test_patch_client(self):
        initial_client = Clients.objects.last()


class CarsAPITestCase(AuthorizedAPITestCase, TestWithCar):
    """
    A class that tests view that support the Cars model.
    CarsAPI (name=cars) -> GET, POST, PUT
    """
    def setUp(self):
        super(CarsAPITestCase, self).setUp()
        # client-user (necessary to receive a token)
        self.user_data = {'username': 'Username', 'password': 'some_pass'}
        user = User.objects.create_user(**self.user_data)
        Clients.objects.create_client(user=user, avatar=None)

    def test_get(self):
        response = self.client.get(reverse('car_rental:cars'))

        self.assertEqual(response.status_code, 200)

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

        # get token:
        token = self.get_token(self.user_data)

        response = self.client.post(
            reverse('car_rental:cars'),
            new_car_data,
            HTTP_AUTHORIZATION=token,
        )
        cars = Cars.objects.all()

        self.assertEqual(response.status_code, 201)
        self.assertEqual(len(cars), 2)
        self.assertIn('token', response.data)

    def test_incorrect_post(self):
        # copy car data
        new_car_data = self.car_data

        # change fields to create dict for incorrect request
        new_car_data['id'] += 1
        new_car_data['segment'] = self.segment_id
        new_car_data['reg_number'] += 'xxxxx'  # too long reg number

        # get token:
        token = self.get_token(self.user_data)

        response = self.client.post(
            reverse('car_rental:cars'),
            new_car_data,
            HTTP_AUTHORIZATION=token,
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn('token', response.data)  # refresh token even when 400

    def test_correct_put(self):
        updated_car_data = self.car_data
        updated_car_data['brand'] = 'other brand'  # change brand
        updated_car_data['segment'] = self.segment_id

        # get token:
        token = self.get_token(self.user_data)

        response = self.client.put(
            reverse('car_rental:cars'),
            updated_car_data,
            HTTP_AUTHORIZATION=token,
        )
        cars = Cars.objects.all()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(cars[0].brand, updated_car_data['brand'])
        self.assertIn('token', response.data)

    def test_incorrect_put(self):
        updated_car_data = self.car_data
        updated_car_data['reg_number'] = 'to_long_reg_number'  # change brand
        updated_car_data['segment'] = self.segment_id

        # get token:
        token = self.get_token(self.user_data)

        response = self.client.put(
            reverse('car_rental:cars'),
            updated_car_data,
            HTTP_AUTHORIZATION=token
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn('token', response.data)  # refresh token even when 400


class DeleteCarAPITestCase(AuthorizedAPITestCase, TestWithCar):
    def setUp(self):
        super(DeleteCarAPITestCase, self).setUp()
        # client-user (necessary to receive a token)
        self.user_data = {'username': 'Username', 'password': 'some_pass'}
        user = User.objects.create_user(**self.user_data)
        Clients.objects.create_client(user=user, avatar=None)

    def test_del_car(self):
        # get token:
        token = self.get_token(self.user_data)

        url = reverse('car_rental:cars', kwargs={'pk': self.car_data['id']})
        response = self.client.delete(url, HTTP_AUTHORIZATION=token)

        self.assertEqual(response.status_code, 200)
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
        Clients.objects.create_client(user=user, avatar=None)

    def test_get(self):
        response = self.client.get(reverse('car_rental:segments'))

        self.assertEqual(response.status_code, 200)

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

        # get token:
        token = self.get_token(self.user_data)

        response = self.client.post(
            reverse('car_rental:segments'),
            data=json.dumps(new_segment_data),
            content_type='application/json',
            HTTP_AUTHORIZATION=token,
        )
        segments = Segments.objects.all()

        self.assertEqual(response.status_code, 201)
        self.assertEqual(len(segments), 2)
        self.assertIn('token', response.data)

    def test_unauthorized_post(self):
        response = self.client.post(
            reverse('car_rental:segments'),
            data=json.dumps({}),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 401)

    def test_incorrect_post(self):
        # copy segment data
        new_segment_data = self.segment_data

        # change fields to create dict for request
        new_segment_data['id'] += 1
        new_segment_data['pricing'] = self.pricing_data
        new_segment_data['pricing']['hour'] = 'text'  # wrong type

        # get token:
        token = self.get_token(self.user_data)

        response = self.client.post(
            reverse('car_rental:segments'),
            data=json.dumps(new_segment_data),
            content_type='application/json',
            HTTP_AUTHORIZATION=token,
        )
        segments = Segments.objects.all()

        self.assertEqual(response.status_code, 400)
        self.assertEqual(len(segments), 1)
        self.assertIn('token', response.data)


class PutDeleteSegmentAPITestCase(AuthorizedAPITestCase):
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
            'id': 25,
            'name': 'example_name',
            'pricing': self.pricing
        }
        self.segment = Segments.objects.create(**self.segment_data)

        # client-user (necessary to receive a token)
        self.user_data = {'username': 'Username', 'password': 'some_pass'}
        user = User.objects.create_user(**self.user_data)
        Clients.objects.create_client(user=user, avatar=None)

    def test_correct_put(self):
        updated_segment_data = self.segment_data
        updated_segment_data['pricing'] = self.pricing_data
        updated_segment_data['name'] = 'other name'  # change the name

        # get token
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

        self.assertEqual(response.status_code, 200)
        self.assertEqual(segments.count(), 1)  # still 1 object
        self.assertEqual(response.data['name'], updated_segment_data['name'])
        self.assertIn('token', response.data)

    def test_incorrect_put(self):
        updated_segment_data = self.segment_data
        updated_segment_data['pricing'] = self.pricing_data
        updated_segment_data['pricing']['week'] = 'text'  # wrong format

        # get token
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

        self.assertEqual(response.status_code, 400)
        # name unchanged
        self.assertEqual(segments[0].name, self.segment_data['name'])

    def test_del_segment(self):
        # get token
        token = self.get_token(self.user_data)

        url = reverse(
            'car_rental:segments_pk',
            kwargs={'pk': self.segment_data['id']}
        )
        response = self.client.delete(url, HTTP_AUTHORIZATION=token)

        self.assertEqual(response.status_code, 202)
        self.assertEqual(Segments.objects.all().count(), 0)
        self.assertIn('token', response.data)


# VIEWS
class MainTestCase(TestCase):
    """
    Test of the basic view loading Angular static files.
    """
    def test_main_view(self):
        response = Client().get(reverse('car_rental:main'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'car_rental/index.html')


# URLs

class URLTestCase(TestCase):
    def test_main(self):
        name = resolve('/').view_name
        self.assertEqual(name, 'car_rental:main')

    def test_sign_up(self):
        name = resolve('/signup').view_name
        self.assertEqual(name, 'car_rental:sign_up')

    def test_cars(self):
        name = resolve('/cars').view_name
        self.assertEqual(name, 'car_rental:cars')

    def test_del_car(self):
        url = '/cars/10'
        name = resolve(url).view_name
        self.assertEqual(name, 'car_rental:cars')
        self.assertEqual(reverse('car_rental:cars', kwargs={'pk': 10}), url)

    def test_segments(self):
        name = resolve('/segments').view_name
        self.assertEqual(name, 'car_rental:segments')

    def test_del_segment(self):
        url = '/segments/9'
        name = resolve(url).view_name
        self.assertEqual(name, 'car_rental:segments_pk')
        self.assertEqual(reverse(
            'car_rental:segments_pk',
            kwargs={'pk': 9}), url
        )


# MODELS

class ClientTestCase(TestCase):
    def setUp(self):
        user = User.objects.create_user(username='abc', password='some_pass')
        Clients.objects.create_client(user=user, avatar=None)

    def test_client_creation(self):
        client = Clients.objects.last()
        print(Clients.objects.all())
        self.assertIsNotNone(client)
        self.assertIsInstance(client, Clients)
        self.assertTrue(client.user.has_perm('car_rental.client'))

    def test_adding_discounts(self):
        client = Clients.objects.last()
        discount = Discounts.objects.create(
            discount_code=12345,
            discount_value=0.5
        )
        client.discount.add(discount)

        self.assertEqual(client.discount.count(), 1)
        self.assertEqual(
            client.discount.first().discount_code,
            discount.discount_code
        )
        self.assertEqual(
            client.discount.first().discount_value,
            discount.discount_value
        )


class DiscountsTestCase(TestCase):
    def setUp(self):
        Discounts.objects.create(
            discount_code=223344,
            discount_value=0.25
        )

    def test_discount(self):
        """
        Values are rigidly given, to test class attributes
        values: MIN/MAX_CODE.
        """
        discount = Discounts.objects.last()

        self.assertEqual(Discounts.MIN_CODE, 1000)
        self.assertEqual(Discounts.MAX_CODE, 9999999999999)

        self.assertIsNotNone(discount)
        self.assertIsInstance(discount, Discounts)

        self.assertIsInstance(discount.discount_code, int)
        self.assertIsInstance(discount.discount_value, float)

    def test_discount_value_validation(self):
        """
        Values retrieved from class attributes. Only validation is tested.
        """
        # discount_code too small
        min_value = Discounts.MIN_CODE
        discount_data = {'discount_code': min_value - 1,
                         'discount_value': 0.25}
        with self.assertRaises(django.core.exceptions.ValidationError):
            Discounts.objects.create(**discount_data)
        # discount_code too big
        min_value = Discounts.MAX_CODE
        discount_data = {'discount_code': min_value + 1,
                         'discount_value': 0.25}
        with self.assertRaises(django.core.exceptions.ValidationError):
            Discounts.objects.create(**discount_data)

    def test_discount_code_validation(self):
        # discount_value too small
        discount_data = {'discount_code': 12345, 'discount_value': 0.00}
        with self.assertRaises(django.core.exceptions.ValidationError):
            Discounts.objects.create(**discount_data)
        # discount_value too big
        discount_data = {'discount_code': 12345, 'discount_value': 1.01}
        with self.assertRaises(django.core.exceptions.ValidationError):
            Discounts.objects.create(**discount_data)


class PriceListsTestCase(TestCase):
    def setUp(self):
        self.pricing_data = {'hour': 19.99, "day": 99.50, 'week': 389.00}
        PriceLists.objects.create(**self.pricing_data)

    def test_pricing_creation(self):
        pricing = PriceLists.objects.last()

        self.assertIsNotNone(pricing)
        self.assertIsInstance(pricing, PriceLists)

        self.assertEqual(pricing.hour, self.pricing_data['hour'])
        self.assertEqual(pricing.day, self.pricing_data['day'])
        self.assertEqual(pricing.week, self.pricing_data['week'])

    def test_pricing_validation(self):
        # hourly price higher than daily
        pricing_data = {'hour': 19.99, "day": 10.50, 'week': 389.00}
        with self.assertRaises(django.core.exceptions.ValidationError):
            PriceLists.objects.create(**pricing_data)

        # daily price higher than weekly
        pricing_data = {'hour': 19.99, "day": 1000.00, 'week': 389.00}
        with self.assertRaises(ValidationError):
            PriceLists.objects.create(**pricing_data)


class SegmentsTestCase(TestCase):
    def setUp(self):
        self.pricing_data = {
            'id': 14,
            'hour': 25.50,
            'day': 115.99,
            'week': 420.00
        }
        self.pricing = PriceLists.objects.create(**self.pricing_data)

        self.segment_id = 5
        self.name = 'example_name'
        Segments.objects.create(
            id=self.segment_id,
            name=self.name,
            pricing=self.pricing
        )

    def test_segment_creation(self):
        segment = Segments.objects.last()

        self.assertIsInstance(segment, Segments)
        self.assertEqual(segment.name, self.name)

        self.assertEqual(segment.name, self.name)
        self.assertEqual(segment.id, self.segment_id)
        self.assertEqual(segment.pricing.id, self.pricing_data['id'])

    def test_cascade_del(self):
        self.pricing.delete()
        segment = Segments.objects.filter(id=self.segment_id)

        # check segment cascade del
        self.assertEqual(len(segment), 0)


class CarsTestCase(TestWithCar):
    def setUp(self):
        super(CarsTestCase, self).setUp()

    def test_car_creation(self):
        car = Cars.objects.last()
        self.assertIsInstance(car, Cars)
        self.assertEqual(car.segment, self.segment)

        self.assertEqual(car.brand, self.car_data['brand'])
        self.assertEqual(car.model, self.car_data['model'])
        self.assertEqual(car.reg_number, self.car_data['reg_number'])

    def test_cascade_del(self):
        self.segment.delete()
        car = Cars.objects.filter(id=self.car_data['id'])

        # check segment cascade del
        self.assertEqual(len(car), 0)


class OrdersTestCase(TestCase):
    def setUp(self):
        user = User.objects.create_user(username='abc', password='some_pass')
        self.client = Clients.objects.create_client(user=user, avatar=None)
        self.order_data = {
            'client': self.client,
            'cost': 120.00,
            'paid': True,
            'canceled': False,
            'payment_id': 'abc123',
            'comments': 'some comment'
        }
        Orders.objects.create(**self.order_data)

    def test_order_creation(self):
        order = Orders.objects.last()

        self.assertIsInstance(order, Orders)
        self.assertEqual(order.client, self.client)
        self.assertEqual(order.payment_id, self.order_data['payment_id'])

    def test_cancel_order(self):
        order = Orders.objects.last()
        order.cancel_order()

        self.assertTrue(order.canceled)
        self.assertEqual(
            order.comments,
            self.order_data['comments'] + '  - CANCELED!' +
            ' (Order without reservation)'
        )

    def test_validation_order(self):
        """
        An order without a payment_id cannot be marked as paid.
        """
        order = Orders.objects.last()
        order.payment_id = None
        order.paid = True
        with self.assertRaises(ValidationError):
            order.save()


class ReservationTestCase(TestWithCar):
    def setUp(self):
        super(ReservationTestCase, self).setUp()
        user = User.objects.create_user(username='abc', password='some_pass')
        self.client = Clients.objects.create_client(user=user, avatar=None)
        self.order_data = {
            'client': self.client,
            'cost': 120.00,
            'paid': True,
            'canceled': False,
            'payment_id': 'abc123',
            'comments': 'some comment'
        }
        self.order = Orders.objects.create(**self.order_data)
        Reservations.objects.create(
            car=self.car,
            begin=date.today(),
            end=date.today()+datetime.timedelta(days=4),
            order=self.order,
        )

    def test_reservation_creation(self):
        reservation = Reservations.objects.last()
        self.assertIsInstance(reservation, Reservations)
        self.assertEqual(
            reservation.car.segment.pricing.hour,
            self.car.segment.pricing.hour
        )
        self.assertEqual(reservation.order.paid, self.order_data['paid'])

    def test_past_booking_validation(self):
        # past booking
        reservation = Reservations.objects.last()
        reservation.begin = date.today()+datetime.timedelta(days=-14)
        reservation.end = date.today() + datetime.timedelta(days=-10)
        with self.assertRaises(ValidationError):
            reservation.save()

    def test_wrong_range_validation(self):
        # begin later than end
        reservation = Reservations.objects.last()
        reservation.begin = date.today() + datetime.timedelta(days=10)
        reservation.end = date.today() + datetime.timedelta(days=6)
        with self.assertRaises(ValidationError):
            reservation.save()

    def test_busy_term_validation(self):
        reservation = Reservations.objects.last()
        other_reservation = reservation
        with self.assertRaises(ValidationError):
            other_reservation.save()


# MANAGERS

class ClientManagerTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='some_username',
            password='some_password'
        )

    def test_client_manager(self):
        client = Clients.objects.create_client(user=self.user, avatar=None)
        self.assertIsInstance(client, Clients)
        self.assertEqual(self.user, client.user)
        self.assertTrue(client.user.has_perm('car_rental.client'))


# MIDDLEWARE

class SomeMiddlewareTestCase:
    pass
