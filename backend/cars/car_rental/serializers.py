import datetime

from django.db import transaction
from rest_framework import serializers
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import ValidationError

from .models import Segments, Cars, PriceLists, Clients, Reservations, \
    Discounts


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password']


class DiscountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Discounts
        fields = '__all__'


class ClientSerializer(serializers.ModelSerializer):
    user = UserSerializer(many=False)
    avatar = serializers.FileField(required=False)
    discount = DiscountSerializer(many=True, required=False)

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
        fields = ['user', 'avatar', 'discount']


class PriceListSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()

    class Meta:
        model = PriceLists
        fields = '__all__'


class SegmentSerializer(serializers.ModelSerializer):
    pricing = PriceListSerializer(many=False)

    def create(self, validated_data):
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
        fields = '__all__'


class CreateCarSerializer(serializers.Serializer):
    id = serializers.CharField(required=False, max_length=9)
    brand = serializers.CharField(required=True, max_length=64)
    model = serializers.CharField(required=True, max_length=32)
    reg_number = serializers.CharField(required=True, max_length=8)
    img = serializers.FileField(required=False)
    description = serializers.CharField(required=False, max_length=2048)
    segment = serializers.CharField(max_length=8)

    def create(self, validated_data):
        segment = get_object_or_404(
            Segments,
            id=int(validated_data['segment'])
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
    segment = serializers.IntegerField()

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
        cars = Cars.objects.select_related().filter(
            segment=validated_data['segment']
        )
        for car in cars:
            try:
                reservation = Reservations.objects.create(
                    begin=validated_data['begin'],
                    end=validated_data['end'],
                    car=car
                )
                return reservation
            except ValidationError:
                pass
        raise ValidationError('no free car')

    def update(self, instance, validated_data):
        pass


class ReservationSerializer(serializers.ModelSerializer):
    car = CarSerializer(many=False)

    class Meta:
        model = Reservations
        fields = '__all__'
