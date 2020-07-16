from rest_framework import serializers
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from .models import Segments, Cars, PriceLists


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password']


class PriceListSerializer(serializers.ModelSerializer):

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

    class Meta:
        model = Segments
        fields = ['id', 'name', 'pricing']


class CarSerializer(serializers.ModelSerializer):
    segment = SegmentSerializer(many=False)

    class Meta:
        model = Cars
        fields = '__all__'


class CreateCarSerializer(serializers.Serializer):
    brand = serializers.CharField(required=True, max_length=64)
    model = serializers.CharField(required=True, max_length=32)
    regNumber = serializers.CharField(required=True, max_length=8)
    img = serializers.FileField(required=False,)
    description = serializers.CharField(max_length=2048, required=False)
    segment = serializers.CharField(max_length=8)

    def create(self, validated_data):
        segment = get_object_or_404(
            Segments,
            id=int(validated_data['segment'])
        )
        if 'description' not in validated_data:
            validated_data['description'] = ''
        car = Cars.objects.create(
            brand=validated_data['brand'],
            model=validated_data['model'],
            reg_number=validated_data['regNumber'],
            segment=segment,
            img=validated_data['img'],
            description=validated_data['description']
        )
        return car
