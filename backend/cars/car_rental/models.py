from django.db import models
from django.core.validators import MinLengthValidator, MaxValueValidator, \
    MinValueValidator
from django.contrib.auth.models import User
from django.contrib.auth.models import Permission

# MANAGER CUSTOMIZATION


class ClientManager(models.Manager):
    def create_client(self, user):
        client = self.create(user=user)
        client_perm = Permission.objects.get(name='clients_permission')
        user.user_permissions.add(client_perm)
        return client


# MODELS


class Discounts(models.Model):
    discount_code = models.IntegerField(
        validators=[MaxValueValidator(999), MinValueValidator(99999999)],
    )
    discount_value = models.FloatField(
        validators=[MaxValueValidator(0.1), MinValueValidator(0.99)],
    )


class Clients(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    discount = models.ManyToManyField(Discounts)

    objects = ClientManager()

    class Meta:
        permissions = (
            ('client', 'clients_permission'),
        )
