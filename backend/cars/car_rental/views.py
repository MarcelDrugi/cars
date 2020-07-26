"""
Backend API documentation on '/swagger.json' or '/swagger.yaml'
"""
import datetime

from django.core.files.storage import FileSystemStorage
from django.db import transaction
from django.contrib.auth.models import User
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
from .models import Clients, PriceLists, Segments, Cars, Reservations
from .serializers import UserSerializer, SegmentSerializer, \
    CreateCarSerializer, CarSerializer, ClientSerializer, \
    CheckReservationSerializer, ReservationSerializer, AvatarSerializer


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
            except Exception as exc:
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

class CarsAPI(TokenRefresh, ListModelMixin):
    """
    Handles :model:`car_rental:Cars` for GET/POST/PUT requests.
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
        print('cars auth : ', self.authentication_classes)
        print('cars perm : ', self.permission_classes)
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


class DeleteCarAPI(TokenRefresh, DestroyModelMixin):
    """
    Handles :model:`car_rental:Cars` for DELETE requests.
    """
    permission_classes = (IsAuthenticated,)

    def delete(self, request, pk):
        try:
            car_to_del = Cars.objects.get(pk=pk)
            car_to_del.delete()
            return Response(
                {'token': self._take_new_token()},
                status=status.HTTP_202_ACCEPTED
            )
        except (Cars.DoesNotExist, AttributeError) as exc:
            return Response(
                {'token': self._take_new_token()},
                status=status.HTTP_400_BAD_REQUEST
            )


class SegmentsAPI(TokenRefresh, ListModelMixin):
    """
    Handles :model:`car_rental:Segments` and the assigned
    :model:`car_rental.PriceLists` for GET/POST requests.
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


class PutDeleteSegmentAPI(TokenRefresh, DestroyModelMixin, UpdateModelMixin):
    """
    Handles :model:`car_rental:Segments` and the assigned
    :model:`car_rental.PriceLists` for PUT/DELETE requests.
    """

    permission_classes = (IsAuthenticated, )
    queryset = Segments.objects.select_related().all()
    serializer_class = SegmentSerializer

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
    permission_classes = (IsAuthenticated, )

    def post(self, request, *args, **kwargs):
        check_serialized = CheckReservationSerializer(data=request.data)
        if check_serialized.is_valid():
            try:
                reservation = check_serialized.save()
            except ValidationError:
                return Response(
                    {'token': self._take_new_token()},
                    status=status.HTTP_409_CONFLICT
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
                        'reservation': reservation.id,
                        'client': serialized_client.data,
                     },
                    status=status.HTTP_201_CREATED
                )
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class ReservationAPI(TokenRefresh):
    permission_classes = ()

    def get(self, request, **kwargs):
        print('jestem')
        try:
            reservation = Reservations.objects.get(id=kwargs['id'])
            print(reservation)
            serialized_reservation = ReservationSerializer(reservation)
            print(serialized_reservation.data)
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
