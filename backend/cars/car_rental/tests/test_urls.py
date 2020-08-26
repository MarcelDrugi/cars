from django.test import TestCase
from django.urls import resolve, reverse


class URLTestCase(TestCase):
    def test_main(self):
        name = resolve('/').view_name
        self.assertEqual(name, 'car_rental:main')

    def test_sign_up(self):
        name = resolve('/signup').view_name
        self.assertEqual(name, 'car_rental:sign_up')

    def test_client_with_id(self):
        pk = '3'
        url = '/client/' + pk
        name = resolve(url).view_name
        self.assertEqual(name, 'car_rental:client_pk')
        self.assertEqual(
            reverse('car_rental:client_pk', kwargs={'pk': pk}),
            url
        )

    def test_client_with_username(self):
        username = 'some_username'
        url = '/client/single/' + username
        name = resolve(url).view_name
        self.assertEqual(name, 'car_rental:client')
        self.assertEqual(
            reverse('car_rental:client', kwargs={'username': username}),
            url
        )

    def test_cars(self):
        name = resolve('/cars').view_name
        self.assertEqual(name, 'car_rental:cars')

    def test_del_car(self):
        pk = '10'
        url = '/cars/' + pk
        name = resolve(url).view_name
        self.assertEqual(name, 'car_rental:cars')
        self.assertEqual(reverse('car_rental:cars', kwargs={'pk': pk}), url)

    def test_segments(self):
        name = resolve('/segments').view_name
        self.assertEqual(name, 'car_rental:segments')

    def test_del_segment(self):
        pk = '9'
        url = '/segments/' + pk
        name = resolve(url).view_name
        self.assertEqual(name, 'car_rental:segments_pk')
        self.assertEqual(reverse(
            'car_rental:segments_pk',
            kwargs={'pk': pk}), url
        )

    def test_single_segment(self):
        id = '5'
        url = '/segment/' + id
        name = resolve(url).view_name
        self.assertEqual(name, 'car_rental:segment')
        self.assertEqual(reverse('car_rental:segment', kwargs={'id': id}), url)

    def test_check_reservation(self):
        url = '/checkres'
        name = resolve(url).view_name
        self.assertEqual(name, 'car_rental:check_res')

    def test_reservation(self):
        pk = '2275'
        url = '/reservation/' + pk
        name = resolve(url).view_name
        self.assertEqual(name, 'car_rental:reservation')
        self.assertEqual(reverse('car_rental:reservation', kwargs={'pk': pk}), url)

    def test_client_reservation(self):
        name = resolve('/reservation').view_name
        self.assertEqual(name, 'car_rental:client_reservation')

    def test_clients(self):
        name = resolve('/clients').view_name
        self.assertEqual(name, 'car_rental:clients')

    def test_terms(self):
        car_id = '19'
        url = '/terms/' + car_id
        name = resolve(url).view_name
        self.assertEqual(name, 'car_rental:terms')
        self.assertEqual(
            reverse('car_rental:terms', kwargs={'car_id': car_id}),
            url
        )

    def test_discounts(self):
        name = resolve('/discounts').view_name
        self.assertEqual(name, 'car_rental:discounts')

    def test_discounts_pk(self):
        pk = '29'
        url = '/discounts/' + pk
        name = resolve(url).view_name
        self.assertEqual(name, 'car_rental:discounts_pk')
        self.assertEqual(
            reverse('car_rental:discounts_pk', kwargs={'pk': pk}),
            url
        )

    def test_new_order(self):
        name = resolve('/order').view_name
        self.assertEqual(name, 'car_rental:new_order')

    def test_existing_order(self):
        pk = '1088'
        url = '/order/' + pk
        name = resolve(url).view_name
        self.assertEqual(name, 'car_rental:existing_order')
        self.assertEqual(
            reverse('car_rental:existing_order', kwargs={'pk': pk}),
            url
        )
