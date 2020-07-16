from django.core.files.storage import FileSystemStorage
from django.db import transaction
from django.contrib.auth.models import User
from django.views.generic import TemplateView
from django.shortcuts import get_object_or_404
from rest_framework.generics import CreateAPIView, GenericAPIView
from rest_framework.mixins import ListModelMixin, CreateModelMixin
from rest_framework.parsers import FileUploadParser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from .models import Clients, PriceLists, Segments, Cars
from .serializers import UserSerializer, SegmentSerializer, \
    CreateCarSerializer, CarSerializer


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
    def create(self, request, **kwargs):
        serialized = UserSerializer(data=request.data)
        if serialized.is_valid():
            try:
                with transaction.atomic():
                    user = User.objects.create_user(
                        first_name=serialized.initial_data['first_name'],
                        last_name=serialized.initial_data['last_name'],
                        email=serialized.initial_data['email'],
                        username=serialized.initial_data['username'],
                        password=serialized.initial_data['password'],
                    )
                    Clients.objects.create_client(user=user)
                return Response(
                    serialized.data,
                    status=status.HTTP_201_CREATED
                )
            except User.DoesNotExist:
                return Response(
                    serialized.errors,
                    status=status.HTTP_507_INSUFFICIENT_STORAGE
                )
            except:
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


class Test(APIView):
    def get(self, request, **kwargs):
        refreshed_token = None
        if 'new_token' in request.META:
            refreshed_token = request.META['new_token']
        return Response(
            {
                'odpowiedz': 'sukces',
                'refreshed_token': refreshed_token
            },
            status=status.HTTP_200_OK
        )


class CarsAPI(TokenRefresh, CreateModelMixin, ListModelMixin):
    serializer_class = CarSerializer
    queryset = Segments.objects.select_related().all()

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


class SegmentsAPI(TokenRefresh, ListModelMixin, CreateModelMixin):
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