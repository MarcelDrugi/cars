from django.db import transaction
from django.contrib.auth.models import User
from django.views.generic import TemplateView
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from .models import Clients
from .serializers import UserSerializer


class MainView(TemplateView):
    template_name = 'car_rental/index.html'


class SignUp(CreateAPIView):
    def post(self, request, **kwargs):
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
