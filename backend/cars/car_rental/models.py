from django.db import models
from django.core.validators import MinLengthValidator, MaxValueValidator, \
    MinValueValidator, MaxLengthValidator
from django.contrib.auth.models import User
from .managers import ClientManager


class Discounts(models.Model):
    discount_code = models.IntegerField(
        validators=[MinValueValidator(999), MinValueValidator(99999999)],
    )
    discount_value = models.FloatField(
        validators=[MinValueValidator(0.1), MaxValueValidator(0.99)],
    )

    def __str__(self):
        return 'discount nr: ' + str(self.discount_code)


class Clients(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    discount = models.ManyToManyField(Discounts)

    objects = ClientManager()

    def __str__(self):
        return 'client: ' + self.user.username


class PriceLists(models.Model):
    hour = models.FloatField()
    day = models.FloatField()
    week = models.FloatField()


class Segments(models.Model):
    name = models.CharField(
        max_length=16,
        validators=[MinLengthValidator(1)],
        help_text='Select type of car'
    )
    pricing = models.ForeignKey(
        PriceLists,
        on_delete=models.CASCADE,
        blank=True,
        null=True
    )


class Cars(models.Model):
    brand = models.CharField(max_length=64)
    model = models.CharField(max_length=32)
    reg_number = models.CharField(max_length=8)
    segment = models.ForeignKey(
        Segments,
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        related_name='car_segment'
    )
    img = models.FileField(null=True, blank=True)
    description = models.CharField(max_length=2048, blank=True, null=True)

    def __str__(self):
        return self.brand + ' ' + self.model + ' (' + self.reg_number + ')'
