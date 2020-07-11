"""
Unit tests.
File divided into 4 parts: View, URLs, Models, Managers, Middleware and
Serializers tests.
"""
from django.test import TestCase, Client
from django.urls import reverse, resolve
import json
from rest_framework.exceptions import ErrorDetail
from rest_framework.test import APITestCase
from .models import *


# VIEWS
from .serializers import UserSerializer


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
        self.assertEqual(response.data, reg_data)

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


# URLs

class URLTestCase(TestCase):
    def test_main(self):
        name = resolve('/').view_name
        self.assertEqual(name, 'car_rental:main')

    def test_sign_up(self):
        name = resolve('/signup').view_name
        self.assertEqual(name, 'car_rental:sign_up')


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
