import datetime
from datetime import date
import django
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.test import TestCase
from car_rental.models import Clients, Discounts, PriceLists, Segments, Cars, \
    Orders, Reservations
from car_rental.tests.shared import TestWithCar


class ClientTestCase(TestCase):
    def setUp(self):
        user = User.objects.create_user(username='abc', password='some_pass')
        Clients.objects.create_client(user=user, avatar=None)

    def test_client_creation(self):
        client = Clients.objects.last()
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
