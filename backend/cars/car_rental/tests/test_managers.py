from unittest import TestCase
from django.contrib.auth.models import User
from car_rental.models import Clients


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
