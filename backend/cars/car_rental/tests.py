"""
Unit tests.
File divided into 4 parts: View, URLs, Models, Managers, Middleware and
Serializers tests.
"""
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, Client
from django.urls import reverse, resolve
import json
from rest_framework.exceptions import ErrorDetail
from rest_framework.test import APITestCase
from .models import *
from .serializers import UserSerializer


# VIEWS

class SignUpTestCase(APITestCase):
    """
    Test of API-view used for user registration.
    """
    # correct request
    def test_ok_request(self):
        reg_data = {
            'first_name': 'Jan',
            'last_name': 'Kowalski',
            'email': 'jan@kowalski.pl',
            'username': 'some_username',
            'password': 'some_password',
        }

        response = self.client.post(reverse('car_rental:sign_up'), reg_data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['first_name'], reg_data['first_name'])
        self.assertEqual(response.data['last_name'], reg_data['last_name'])
        self.assertEqual(response.data['username'], reg_data['username'])
        self.assertEqual(response.data['email'], reg_data['email'])

    # incorrect request
    def test_not_ok_request(self):
        reg_data = {
            'first_name': 'Jan',
            'last_name': 'Kowalski',
            'email': 'jan@kowalski,pl',  # invalid email format
            'username': 'some_username',
            'password': 'some_password',
        }

        response = self.client.post(reverse('car_rental:sign_up'), reg_data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.data['email'][0],
            ErrorDetail(string='Enter a valid email address.', code='invalid'))


class MainTestCase(TestCase):
    """
    Test of the basic view loading Angular static files.
    """
    def test_main_view(self):
        response = Client().get(reverse('car_rental:main'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'car_rental/index.html')


class CarsAPITestCase(APITestCase):
    """
    A class that tests view that support the Cars model.
    CarsAPI (name=cars) -> GET, POST, PUT
    """
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

        response = self.client.post(reverse('car_rental:cars'), new_car_data)
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

        response = self.client.post(reverse('car_rental:cars'), new_car_data)
        self.assertEqual(response.status_code, 400)
        self.assertIn('token', response.data)  # refresh token even when 400

    def test_correct_put(self):
        updated_car_data = self.car_data
        updated_car_data['brand'] = 'other brand'  # change brand
        updated_car_data['segment'] = self.segment_id

        response = self.client.put(
            reverse('car_rental:cars'),
            updated_car_data
        )
        cars = Cars.objects.all()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(cars[0].brand, updated_car_data['brand'])
        self.assertIn('token', response.data)

    def test_incorrect_put(self):
        updated_car_data = self.car_data
        updated_car_data['reg_number'] = 'to_long_reg_number'  # change brand
        updated_car_data['segment'] = self.segment_id

        response = self.client.put(
            reverse('car_rental:cars'),
            updated_car_data
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn('token', response.data)  # refresh token even when 400


class DeleteCarAPITestCase(APITestCase):
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

    def test_del_car(self):
        url = reverse('car_rental:del_car', kwargs={'pk': self.car_data['id']})
        response = self.client.delete(url)

        self.assertEqual(response.status_code, 202)
        self.assertEqual(len(Cars.objects.all()), 0)
        self.assertIn('token', response.data)


class SegmentsAPITestCase(APITestCase):
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

        response = self.client.post(
            reverse('car_rental:segments'),
            data=json.dumps(new_segment_data),
            content_type='application/json'
        )
        segments = Segments.objects.all()

        self.assertEqual(response.status_code, 201)
        self.assertEqual(len(segments), 2)
        self.assertIn('token', response.data)

    def test_incorrect_post(self):
        # copy segment data
        new_segment_data = self.segment_data

        # change fields to create dict for request
        new_segment_data['id'] += 1
        new_segment_data['pricing'] = self.pricing_data
        new_segment_data['pricing']['hour'] = 'text'  # wrong type

        response = self.client.post(
            reverse('car_rental:segments'),
            data=json.dumps(new_segment_data),
            content_type='application/json'
        )
        segments = Segments.objects.all()

        self.assertEqual(response.status_code, 400)
        self.assertEqual(len(segments), 1)
        self.assertIn('token', response.data)


class PutDeleteSegmentAPITestCase(APITestCase):
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

    def test_correct_put(self):
        updated_segment_data = self.segment_data
        updated_segment_data['pricing'] = self.pricing_data
        updated_segment_data['name'] = 'other name'  # change the name

        response = self.client.put(
            reverse(
                'car_rental:put_del_segment',
                kwargs={'pk': self.segment_data['id']}
            ),
            data=json.dumps(updated_segment_data),
            content_type='application/json'
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

        response = self.client.put(
            reverse(
                'car_rental:put_del_segment',
                kwargs={'pk': self.segment_data['id']}
            ),
            data=json.dumps(updated_segment_data),
            content_type='application/json'
        )
        segments = Segments.objects.all()

        self.assertEqual(response.status_code, 400)
        # name unchanged
        self.assertEqual(segments[0].name, self.segment_data['name'])

    def test_del_segment(self):
        url = reverse(
            'car_rental:put_del_segment',
            kwargs={'pk': self.segment_data['id']}
        )
        response = self.client.delete(url)

        self.assertEqual(response.status_code, 202)
        self.assertEqual(Segments.objects.all().count(), 0)
        self.assertIn('token', response.data)


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
        url = '/delcar/10'
        name = resolve(url).view_name
        self.assertEqual(name, 'car_rental:del_car')
        self.assertEqual(reverse('car_rental:del_car', kwargs={'pk': 10}), url)

    def test_segments(self):
        name = resolve('/segments').view_name
        self.assertEqual(name, 'car_rental:segments')

    def test_del_segment(self):
        url = '/putdelsegment/9'
        name = resolve(url).view_name
        self.assertEqual(name, 'car_rental:put_del_segment')
        self.assertEqual(
            reverse('car_rental:put_del_segment', kwargs={'pk': 9}),
            url
        )


# MODELS

class ClientTestCase(TestCase):
    def test_client_creation(self):
        user = User.objects.create_user(username='abc', password='some_pass')
        client = Clients.objects.create(user=user)
        self.assertIsNotNone(client)
        self.assertIsInstance(client, Clients)

    def test_adding_discounts(self):
        user = User.objects.create_user(username='abc', password='some_pass')
        client = Clients.objects.create(user=user)
        discount = Discounts.objects.create(
            discount_code=1234,
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
    def test_discount(self):
        discount = Discounts.objects.create(
            discount_code=223344,
            discount_value=0.25
        )
        self.assertIsNotNone(discount)
        self.assertIsInstance(discount, Discounts)

        self.assertIsInstance(discount.discount_code, int)
        self.assertTrue(999 <= discount.discount_code <= 99999999)

        self.assertIsInstance(discount.discount_value, float)
        self.assertTrue(0. < discount.discount_value < 1.)


class PriceListsTestCase(TestCase):
    def test_pricing_creation(self):
        pricing_data = {'hour': 19.99, "day": 99.50, 'week': 389.00}
        pricing = PriceLists.objects.create(**pricing_data)

        self.assertIsNotNone(pricing)
        self.assertIsInstance(pricing, PriceLists)

        self.assertEqual(pricing.hour, pricing_data['hour'])
        self.assertEqual(pricing.day, pricing_data['day'])
        self.assertEqual(pricing.week, pricing_data['week'])


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
        self.segment = Segments.objects.create(
            id=self.segment_id,
            name=self.name,
            pricing=self.pricing
        )

    def test_segment_creation(self):
        self.assertIsInstance(self.segment, Segments)
        self.assertEqual(self.segment.name, self.name)

        self.assertEqual(self.segment.name, self.name)
        self.assertEqual(self.segment.id, self.segment_id)

        self.assertEqual(self.segment.pricing.id, self.pricing_data['id'])
        self.assertEqual(self.segment.pricing.hour, self.pricing_data['hour'])
        self.assertEqual(self.segment.pricing.day, self.pricing_data['day'])
        self.assertEqual(self.segment.pricing.week, self.pricing_data['week'])

    def test_cascade_del(self):
        self.pricing.delete()
        segment = Segments.objects.filter(id=self.segment_id)

        # check segment cascade del
        self.assertEqual(len(segment), 0)


class CarsTestCase(TestCase):
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

    def test_car_creation(self):
        self.assertIsInstance(self.car, Cars)
        self.assertEqual(self.car.segment, self.segment)

        self.assertEqual(self.car.brand, self.car_data['brand'])
        self.assertEqual(self.car.model, self.car_data['model'])
        self.assertEqual(self.car.reg_number, self.car_data['reg_number'])
        self.assertEqual(self.car.description, self.car_data['description'])

    def test_cascade_del(self):
        self.segment.delete()
        car = Cars.objects.filter(id=self.car_data['id'])

        # check segment cascade del
        self.assertEqual(len(car), 0)


# MANAGERS

class ClientManagerTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='some_username',
            password='some_password'
        )

    def test_client_manager(self):
        client = Clients.objects.create_client(user=self.user)
        self.assertIsInstance(client, Clients)
        self.assertEqual(self.user, client.user)
        self.assertTrue(client.user.has_perm('car_rental.client'))


# MIDDLEWARE

class SomeMiddlewareTestCase:
    pass


# SERIALIZERS

class UserSerializerTestCase(TestCase):
    def setUp(self):
        self.user_data = {
            'first_name': 'Carol',
            'last_name': 'Smith',
            'email': 'some@email.ll',
            'username': 'some_username',
            'password': 'some_password'
        }

        self.user_json = json.dumps(self.user_data, ensure_ascii=False)

    def test_user_serialization(self):
        User.objects.create_user(**self.user_data)
        user = User.objects.all()[0]
        serialized_user = UserSerializer(user)
        self.assertIsInstance(serialized_user, UserSerializer)
        self.assertIsInstance(serialized_user.data, dict)
        self.assertEqual(
            serialized_user.data['username'],
            self.user_data['username']
        )

    def test_user_deserialization(self):
        new_user_data = json.loads(self.user_json)
        deserialized_user = UserSerializer(data=new_user_data)
        self.assertTrue(deserialized_user.is_valid())
