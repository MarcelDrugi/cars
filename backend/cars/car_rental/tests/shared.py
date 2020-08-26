from django.test import TestCase
from car_rental.models import PriceLists, Segments, Cars


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
