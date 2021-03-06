import datetime

from django.contrib.auth.models import User
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from .models import (Cars, Clients, Discounts, Orders, PriceLists,
                     Reservations, Segments)


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password']
        extra_kwargs = {'username': {'validators': [UnicodeUsernameValidator]}}


class DiscountSerializer(serializers.ModelSerializer):

    class Meta:
        model = Discounts
        fields = ['id', 'discount_code', 'discount_value']


class ClientSerializer(serializers.ModelSerializer):
    user = UserSerializer(many=False)
    avatar = serializers.FileField(required=False)
    discount = DiscountSerializer(many=True, required=False)

    def __init__(self, *args, **kwargs):
        if 'context' in kwargs:
            if 'skip_fields' in kwargs['context']:
                skip_fields = kwargs['context']['skip_fields']
                kwargs['context'].pop('skip_fields')

                for field in skip_fields:
                    self.fields.pop(field)
        super(ClientSerializer, self).__init__(*args, **kwargs)

    def create(self, validated_data):
        avatar = None
        if 'avatar' in validated_data:
            avatar = validated_data['avatar']

        with transaction.atomic():
            user = User.objects.create_user(**validated_data['user'])

            client = Clients.objects.create_client(
                user=user,
                avatar=avatar
            )
        return client

    class Meta:
        model = Clients
        fields = ['id', 'user', 'avatar', 'discount']


class UpdateClientDataSerializer(serializers.Serializer):
    avatar = serializers.FileField(required=False)
    user = UserSerializer(many=False)

    def to_internal_value(self, data):
        data._mutable = True
        try:
            avatar = data.get('avatar')
            data = {'user': data}
            if avatar is not None and avatar != 'undefined':
                data['avatar'] = avatar
        except KeyError:
            raise ValidationError('Wrong data format')
        return super(UpdateClientDataSerializer, self).to_internal_value(data)

    def update(self, instance, validated_data):
        user = instance.user

        with transaction.atomic():
            user.username = validated_data['user']['username']
            user.first_name = validated_data['user']['first_name']
            user.last_name = validated_data['user']['last_name']
            user.email = validated_data['user']['email']
            user.save()
            if 'avatar' in validated_data:
                instance.avatar = validated_data['avatar']
                instance.save()
        return instance


class AvatarSerializer(serializers.Serializer):
    avatar = serializers.FileField()


class PriceListSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()

    class Meta:
        model = PriceLists
        fields = ['id', 'hour', 'day', 'week']


class SegmentSerializer(serializers.ModelSerializer):
    pricing = PriceListSerializer(many=False)

    def create(self, validated_data):
        with transaction.atomic():
            pricing = PriceLists.objects.create(
                hour=validated_data['pricing']['hour'],
                day=validated_data['pricing']['day'],
                week=validated_data['pricing']['week'],
            )

            segment = Segments.objects.create(
                name=validated_data['name'],
                pricing=pricing
            )
            return segment

    def update(self, instance, validated_data):
        pricing = get_object_or_404(
            PriceLists,
            id=int(validated_data['pricing']['id'])
        )
        with transaction.atomic():
            pricing.hour = validated_data['pricing']['hour']
            pricing.day = validated_data['pricing']['day']
            pricing.week = validated_data['pricing']['week']
            pricing.save()

            instance.name = validated_data['name']
            instance.pricing = pricing
            instance.save()

        return instance

    class Meta:
        model = Segments
        fields = ['id', 'name', 'pricing']


class CarSerializer(serializers.ModelSerializer):
    segment = SegmentSerializer(many=False)

    class Meta:
        model = Cars
        fields = ['id', 'brand', 'model', 'reg_number', 'segment', 'img',
                  'description']


class CreateCarSerializer(serializers.Serializer):
    id = serializers.CharField(required=False, max_length=9)
    brand = serializers.CharField(required=True, max_length=64)
    model = serializers.CharField(required=True, max_length=32)
    reg_number = serializers.CharField(required=True, max_length=8)
    img = serializers.FileField(required=False)
    description = serializers.CharField(required=False, max_length=2048)
    segment = serializers.IntegerField()

    def create(self, validated_data):
        segment = get_object_or_404(
            Segments,
            id=validated_data['segment']
        )
        if 'description' not in validated_data:
            validated_data['description'] = ''
        if 'img' not in validated_data:
            validated_data['img'] = ''
        car = Cars.objects.create(
            brand=validated_data['brand'],
            model=validated_data['model'],
            reg_number=validated_data['reg_number'],
            segment=segment,
            img=validated_data['img'],
            description=validated_data['description']
        )
        return car

    def update(self, instance, validated_data):
        segment = Segments.objects.get(id=int(validated_data['segment']))
        instance.segment = segment
        del validated_data['segment']
        for field in validated_data.items():
            setattr(instance, field[0], field[1])
        instance.save()
        return instance


class CheckReservationSerializer(serializers.Serializer):
    begin = serializers.CharField(max_length=10)
    end = serializers.CharField(max_length=10)
    segment = serializers.IntegerField(required=False)
    car_id = serializers.IntegerField(required=False)

    def __init__(self, permanent, *args, **kwargs):
        self.permanent = permanent
        super(CheckReservationSerializer, self).__init__(*args, **kwargs)

    def validate_begin(self, data):
        try:
            begin = datetime.datetime.strptime(data, "%d.%m.%Y").date()
        except ValueError:
            raise ValidationError('Incorrect begin-date format')
        return begin

    def validate_end(self, data):
        try:
            end = datetime.datetime.strptime(data, "%d.%m.%Y").date()
        except ValueError:
            raise ValidationError('Incorrect end-date format')
        return end

    def validate_segment(self, data):
        try:
            segment = Segments.objects.get(id=data)
        except Segments.DoesNotExist:
            raise ValidationError('Incorrect Segments object id')
        return segment

    def create(self, validated_data):
        if 'segment' in validated_data:
            cars = Cars.objects.select_related().filter(
                segment=validated_data['segment']
            )
            for car in cars:
                try:
                    reservation = Reservations(
                        begin=validated_data['begin'],
                        end=validated_data['end'],
                        car=car
                    )
                    reservation.save()
                except ValidationError:
                    pass
                else:
                    if self.permanent is False:
                        reservation.delete()
                    return reservation
            raise ValidationError('no free car')

        elif 'car_id' in validated_data:
            car = Cars.objects.select_related().get(
                id=validated_data['car_id']
            )
            try:
                reservation = Reservations(
                    begin=validated_data['begin'],
                    end=validated_data['end'],
                    car=car
                )
                reservation.save()
            except ValidationError:
                ValidationError('car is not free in this term')
            else:
                if self.permanent is False:
                    reservation.delete()
                return reservation
        else:
            ValidationError('car or segment is required')

    def update(self, instance, validated_data):
        pass


class ReservationRelatedSerializer(serializers.RelatedField):
    def to_representation(self, data):
        try:
            data['begin'] = datetime.datetime.strptime(data['begin'],
                                                       "%Y-%m-%d").date()
        except ValueError:
            raise ValidationError('Incorrect begin-date format')
        try:
            data['end'] = datetime.datetime.strptime(data['end'],
                                                     "%Y-%m-%d").date()
        except ValueError:
            raise ValidationError('Incorrect end-date format')
        return data

    def to_internal_value(self, data):
        pass


class OrderSerializer(serializers.ModelSerializer):
    client = ClientSerializer(many=False)

    class Meta:
        model = Orders
        fields = ['id', 'client', 'cost', 'paid', 'canceled', 'payment_id',
                  'comments', ]


class ReservationSerializer(serializers.ModelSerializer):
    car = CarSerializer(many=False)
    order = OrderSerializer(many=False, required=False)

    class Meta:
        model = Reservations
        fields = ['id', 'begin', 'end', 'car', 'created_time', 'order']


class MajorOrderDataSerializer(serializers.Serializer):
    reserved_car = serializers.IntegerField()
    begin = serializers.DateField()
    end = serializers.DateField()
    client = serializers.CharField(max_length=128)
    cost = serializers.FloatField()
    comments = serializers.CharField(max_length=2048, required=False)
    discount = serializers.IntegerField(required=False)

    def to_internal_value(self, data):
        if data.get('comments') == '' or data.get('comments') is None:
            data['comments'] = ' - no comments - '
        return super(MajorOrderDataSerializer, self).to_internal_value(data)

    def create(self, validated_data):
        discount = None
        try:
            client = Clients.objects.get(
                user__username=validated_data['client']
            )
        except Clients.DoesNotExist:
            raise ValidationError('Wrong client id')
        if 'discount' in validated_data:
            try:
                discount = Discounts.objects.get(
                    discount_code=validated_data['discount']
                )
            except Discounts.DoesNotExist:
                raise ValidationError('Discount does not exist')

            discounts = client.discount.all()
            if discount not in discounts:
                raise ValidationError('Discount is not assigned to the user')
        try:
            car = Cars.objects.get(id=validated_data['reserved_car'])
        except Cars.DoesNotExist:
            raise ValidationError('Car does not exist')
        with transaction.atomic():
            order = Orders.objects.create(
                client=client,
                cost=validated_data['cost'],
                comments=validated_data['comments']
            )
            reservation = Reservations.objects.create(
                car=car,
                begin=validated_data['begin'],
                end=validated_data['end'],
                order=order,
            )
            if discount:
                client.discount.remove(discount)
        return reservation
