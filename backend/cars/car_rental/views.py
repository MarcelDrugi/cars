"""
Backend API documentation on '/swagger.json' or '/swagger.yaml'
"""
import base64
import datetime
import json

import environ
import requests
from django.core.files.storage import FileSystemStorage
from django.db import transaction
from django.contrib.auth.models import User
from django.urls import reverse
from django.views import View
from django.views.generic import TemplateView
from django.shortcuts import get_object_or_404
from rest_framework.decorators import authentication_classes, \
    permission_classes
from rest_framework.exceptions import ValidationError
from rest_framework.generics import CreateAPIView, GenericAPIView
from rest_framework.mixins import ListModelMixin, CreateModelMixin, \
    UpdateModelMixin, DestroyModelMixin
from rest_framework.parsers import FileUploadParser
from rest_framework.permissions import IsAuthenticatedOrReadOnly, AllowAny, \
    IsAuthenticated
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status, permissions
from django.core import serializers
from paypal.payment_prepare import PaymentLinkGenerator
from .models import Clients, PriceLists, Segments, Cars, Reservations, \
    Discounts, Orders
from .serializers import UserSerializer, SegmentSerializer, \
    CreateCarSerializer, CarSerializer, ClientSerializer, \
    CheckReservationSerializer, ReservationSerializer, AvatarSerializer, \
    DiscountSerializer, MajorOrderDataSerializer


class MainView(TemplateView):
    template_name = 'car_rental/index.html'


class TokenRefresh(GenericAPIView):
    """
    Base class for all endpoints that refresh the authorization token.
    Refreshing occurs in the signal 'request_started'. The token is passed
    from the signal as request's metadata. The _get_new_token () function
    extracts the refreshed token from the metadata and returns as a string.
    """
    def _take_new_token(self):
        refreshed_token = None
        if 'new_token' in self.request.META:
            refreshed_token = self.request.META['new_token']
        return refreshed_token


class SignUp(CreateAPIView):
    """
    Handles :model:`car_rental.Client` and the assigned :model:`auth.User`.
    Contains only one request: POST.
    """
    permission_classes = ()

    def create(self, request, **kwargs):
        print(request.data)
        avatar = request.data['avatar']
        if avatar == 'undefined':
            data = {'user': request.data}
        else:
            data = {'user': request.data, 'avatar': avatar}

        serialized = ClientSerializer(data=data)

        if serialized.is_valid():
            try:
                serialized.save()
                return Response(
                    serialized.data,
                    status=status.HTTP_201_CREATED
                )
            except User.DoesNotExist:
                return Response(
                    serialized.errors,
                    status=status.HTTP_507_INSUFFICIENT_STORAGE
                )
            except Exception:
                return Response(
                    serialized.errors,
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        else:
            if User.objects.filter(username=request.data['username']).exists():
                return Response(
                    serialized.errors,
                    status=status.HTTP_409_CONFLICT
                )
            else:
                return Response(
                    serialized.errors,
                    status=status.HTTP_400_BAD_REQUEST
                )


class AvatarAPI(TokenRefresh):
    def get(self, request, **kwargs):
        try:
            client = Clients.objects.get(user__username=kwargs['username'])
            serialized_avatar = AvatarSerializer({'avatar' : client.avatar})
            return Response(
                {
                    'token': self._take_new_token(),
                    'avatar': serialized_avatar.data
                },
                status=status.HTTP_200_OK
            )
        except Clients.DoesNotExist:
            return Response(
                status=status.HTTP_400_BAD_REQUEST
            )


class ClientsAPI(TokenRefresh, ListModelMixin):
    """
    Handles :model:`car_rental:Clients` for GET/PUT requests.
    """

    serializer_class = ClientSerializer
    queryset = Clients.objects.select_related().all().order_by(
        'user__username'
    )

    def get_serializer_context(self):
        context = super(ClientsAPI, self).get_serializer_context()
        if self.request.method == 'GET':
            context.update({'skip_fields': ['avatar', ]})
        return context

    def get(self, request, **kwargs):
        response = self.list(request, **kwargs)
        response.data.append(
            {'token': self._take_new_token()}
        )
        return response


class DiscountsAPI(TokenRefresh, ListModelMixin, CreateModelMixin, DestroyModelMixin):
    """
    Handles :model:`car_rental:Discounts` for GET/PUT/POST requests.
    GET and POST work os standard.
    For PUT request, view doesnt serialize data, but only checks if objects
    exists and merge them (many-to-many relation)
    """
    serializer_class = DiscountSerializer
    queryset = Discounts.objects.all().order_by('discount_code')

    def get(self, request, **kwargs):
        response = self.list(request, **kwargs)
        response.data.append(
            {'token': self._take_new_token()}
        )
        return response

    def put(self, request, **kwargs):
        try:
            client = Clients.objects.get(user__username=request.data['client'])
            discount = Discounts.objects.get(id=request.data['discount'])
            if request.data['acction'] == 'add':
                client.discount.add(discount)
                client.save()
            else:
                client.discount.remove(discount)
        except (Clients.DoesNotExist, Discounts.DoesNotExist):
            return Response(
                {'token': self._take_new_token()},
                status=status.HTTP_400_BAD_REQUEST
            )
        else:
            return Response(
                {'token': self._take_new_token()},
                status=status.HTTP_200_OK
            )

    def post(self, request, *args, **kwargs):
        self.create(request, *args, **kwargs)
        return Response(
            {'token': self._take_new_token()},
            status=status.HTTP_201_CREATED
        )

    def delete(self, request, *args, **kwargs):
        self.destroy(request, *args, **kwargs)
        return Response(
            {'token': self._take_new_token()},
            status=status.HTTP_200_OK
        )


class CarsAPI(TokenRefresh, ListModelMixin, DestroyModelMixin):
    """
    Handles :model:`car_rental:Cars` for GET/POST/PUT/DELETE requests.
    """

    serializer_class = CarSerializer
    queryset = Cars.objects.select_related().all()

    def get(self, request, **kwargs):
        response = self.list(request, **kwargs)
        response.data.append(
            {'token': self._take_new_token()}
        )
        return response

    def post(self, request, **kwargs):
        serialized = CreateCarSerializer(data=request.data)
        if serialized.is_valid():
            serialized.save()
            return Response(
                {'token': self._take_new_token()},
                status=status.HTTP_201_CREATED
            )
        else:
            return Response(
                {'token': self._take_new_token()},
                status=status.HTTP_400_BAD_REQUEST
            )

    def put(self, request, *args, **kwargs):
        try:
            instance = Cars.objects.get(id=int(request.data['id']))
        except Cars.DoesNotExist:
            return Response(
                {'token': self._take_new_token()},
                status=status.HTTP_204_NO_CONTENT
            )

        serialized = CreateCarSerializer(instance=instance, data=request.data)
        if serialized.is_valid():
            serialized.save()
            return Response(
                {'token': self._take_new_token()},
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                {'token': self._take_new_token()},
                status=status.HTTP_400_BAD_REQUEST
            )

    def delete(self, request, *args, **kwargs):
        self.destroy(request, *args, **kwargs)
        return Response(
            {'token': self._take_new_token()},
            status=status.HTTP_200_OK
        )


class SegmentsAPI(TokenRefresh, ListModelMixin, DestroyModelMixin, UpdateModelMixin):
    """
    Handles :model:`car_rental:Segments` and the assigned
    :model:`car_rental.PriceLists` for GET/POST/PUT/DELETE requests.
    """

    serializer_class = SegmentSerializer
    queryset = Segments.objects.select_related().all()

    def get(self, request, **kwargs):
        response = self.list(request, **kwargs)
        response.data.append(
            {'token': self._take_new_token()}
        )
        return response

    def post(self, request, **kwargs):
        serialized = SegmentSerializer(data=request.data)
        if serialized.is_valid():
            serialized.save()

            return Response(
                {'token': self._take_new_token()},
                status=status.HTTP_201_CREATED
            )
        else:
            return Response(
                {'token': self._take_new_token()},
                status=status.HTTP_400_BAD_REQUEST
            )

    def delete(self, request, *args, **kwargs):
        self.destroy(request, *args, **kwargs)
        return Response(
            {'token': self._take_new_token()},
            status=status.HTTP_202_ACCEPTED
        )

    def put(self, request, *args, **kwargs):
        response = self.update(request, *args, **kwargs)
        response.data['token'] = self._take_new_token()
        return response


class SingleSegmentAPI(TokenRefresh):
    """
    Handles :model:`car_rental:Segments` to GET requests single object.
    """
    def get(self, request, **kwargs):
        try:
            segment = Segments.objects.get(id=kwargs['id'])
            serialized_segment = SegmentSerializer(segment)
        except Segments.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(
                {
                    'token': self._take_new_token(),
                    'segment': serialized_segment.data,
                },
                status=status.HTTP_200_OK,
            )


class CheckReservationAPI(TokenRefresh):
    """
    Handles :model:`car_rental:Reservations` for POST request.
    If serializer has parameter `permanent` equal to False, the view
    doesnt create object. Check availability only.
    View only for authenticated users.
    """
    permission_classes = (IsAuthenticated, )

    def post(self, request, *args, **kwargs):
        check_serialized = CheckReservationSerializer(
            data=request.data,
            permanent=False
        )
        if check_serialized.is_valid():
            try:
                reservation = check_serialized.save()
                serialized_reservation = ReservationSerializer(reservation)
            except ValidationError:
                return Response(
                    {'token': self._take_new_token()},
                    status=status.HTTP_409_CONFLICT
                )
            except AttributeError:
                return Response(
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            else:
                try:
                    client = Clients.objects.get(
                        user__username=request.user.username
                    )
                    serialized_client = ClientSerializer(client)
                except Clients.DoesNotExist:
                    # If the user has passed authentication but cannot be found
                    # in the database, this is an internal server error.
                    return Response(
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR
                    )
                return Response(
                    {
                        'token': self._take_new_token(),
                        'reservation': serialized_reservation.data,
                        'client': serialized_client.data,
                     },
                    status=status.HTTP_201_CREATED
                )
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class ReservationAPI(TokenRefresh, DestroyModelMixin, ):
    """
    Handles :model:`car_rental:Reservations` for GET/DELETE requests.
    View only for authenticated users.
    """
    permission_classes = (IsAuthenticated, )

    queryset = Reservations.objects.select_related().all()

    def get(self, request, **kwargs):
        try:
            reservation = Reservations.objects.get(id=kwargs['pk'])
            serialized_reservation = ReservationSerializer(reservation)
        except Reservations.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(
                {
                    'token': self._take_new_token(),
                    'reservation': serialized_reservation.data,
                },
                status=status.HTTP_200_OK,
            )

    def delete(self, request, *args, **kwargs):
        self.destroy(request, *args, **kwargs)
        return Response(
            {'token': self._take_new_token()},
            status=status.HTTP_202_ACCEPTED
        )


class Order(TokenRefresh):
    def post(self, request, *args, **kwargs):
        env = environ.Env()
        env.read_env('../cars/.env')

        print(self.request.data)
        serialized_major_data = MajorOrderDataSerializer(data=request.data)

        if serialized_major_data.is_valid():
            try:
                reservation = serialized_major_data.save()
            except (ValidationError, TypeError, AttributeError):
                return Response(status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        success_url = request.build_absolute_uri(reverse('success'))
        cancel_url = request.build_absolute_uri(reverse('success'))
        paypal = PaymentLinkGenerator(
            client_id=env('CLIENT_ID'),
            client_secret=env('CLIENT_SECRET'),
            success_url=success_url,
            cancel_url=cancel_url
        )
        data = {
            'name': reservation.car.brand,
            'reg_number': reservation.car.reg_number,
            'value': reservation.order.cost,
        }
        paypal_response = paypal.payment(data)
        print(paypal_response)
        if 'id' in paypal_response:
            payment_link = paypal_response['links'][1]['href']
            order = reservation.order
            order.payment_id = paypal_response['id']
            order.save()
            return Response(
                {
                    'token': self._take_new_token(),
                    'payment_link': payment_link,
                 },
                status=status.HTTP_200_OK,
            )

        return Response(
            status=status.HTTP_200_OK,
        )
