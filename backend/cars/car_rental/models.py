from django.db import models
from django.core.validators import MinLengthValidator, MaxValueValidator, \
    MinValueValidator
from django.contrib.auth.models import User
from .managers import ClientManager


class Discounts(models.Model):
    discount_code = models.IntegerField(
        validators=[MaxValueValidator(999), MinValueValidator(99999999)],
    )
    discount_value = models.FloatField(
        validators=[MaxValueValidator(0.1), MinValueValidator(0.99)],
    )

    def __str__(self):
        return 'discount nr: ' + str(self.discount_code)


class Clients(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    discount = models.ManyToManyField(Discounts)

    objects = ClientManager()

    def __str__(self):
        return 'client: ' + self.user.username
