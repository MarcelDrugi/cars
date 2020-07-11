from django.apps import AppConfig


class CarRentalConfig(AppConfig):
    name = 'car_rental'

    def ready(self):
        from . import signals
