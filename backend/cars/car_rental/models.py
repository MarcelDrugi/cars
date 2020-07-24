from django.db import models
from django.core.validators import MinLengthValidator, MaxValueValidator, \
    MinValueValidator, MaxLengthValidator
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from .managers import ClientManager


class Discounts(models.Model):
    MAX_CODE = 9999999999999
    MIN_CODE = 1000

    discount_code = models.IntegerField(
        validators=[MinValueValidator(MIN_CODE), MinValueValidator(MAX_CODE)],
        unique=True,
    )
    discount_value = models.FloatField(
        validators=[MinValueValidator(0.01), MaxValueValidator(0.99)],
    )

    def save(self, *args, **kwargs):
        self.full_clean()
        super(Discounts, self).save(*args, **kwargs)

    def __str__(self):
        return 'discount nr: ' + str(self.discount_code)


class Clients(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    discount = models.ManyToManyField(Discounts)
    avatar = models.FileField()

    objects = ClientManager()

    def __str__(self):
        return 'client: ' + self.user.username


class PriceLists(models.Model):
    hour = models.FloatField()
    day = models.FloatField()
    week = models.FloatField()

    def clean(self):
        if self.hour > self.day:
            raise ValidationError(
                'The daily charge cannot be less than the hourly charge.'
            )
        if self.day > self.week:
            raise ValidationError(
                'The weekly charge cannot be less than the daily charge.'
            )

        super(PriceLists, self).clean()

    def save(self, *args, **kwargs):
        self.full_clean()
        super(PriceLists, self).save(*args, **kwargs)


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
        null=True,
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


class Reservations(models.Model):
    car = models.ForeignKey(Cars, on_delete=models.CASCADE)
    begin = models.DateField()
    end = models.DateField()

    def _term_checking(self):
        occupied = Reservations.objects.select_related().filter(car=self.car)
        for term in occupied:
            if self.begin > term.end:
                pass
            elif self.end < term.begin:
                pass
            else:
                return False
        return True

    def clean(self):
        if self.begin > self.end:
            raise ValidationError(
                'Wrong dates! End-date must be later than begin-date.'
            )
        if not self._term_checking():
            raise ValidationError(
                'Term is not free'
            )

        super(Reservations, self).clean()

    def save(self, *args, **kwargs):
        self.full_clean()
        super(Reservations, self).save(*args, **kwargs)


class Orders(models.Model):
    client = models.OneToOneField(Clients, on_delete=models.CASCADE)
    cost = models.FloatField(validators=[MinValueValidator(0.01)])
    paid = models.BooleanField(default=False)
    canceled = models.BooleanField(default=False)
