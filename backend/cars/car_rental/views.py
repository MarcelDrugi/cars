from django.core.files.storage import FileSystemStorage
from django.db import transaction
from django.contrib.auth.models import User
from django.views.generic import TemplateView
from django.shortcuts import get_object_or_404
from rest_framework.generics import CreateAPIView, GenericAPIView
from rest_framework.mixins import ListModelMixin, CreateModelMixin, \
    UpdateModelMixin, DestroyModelMixin
from rest_framework.parsers import FileUploadParser
from rest_framework.renderers import JSONRenderer
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


class CarsAPI(TokenRefresh, ListModelMixin):
    serializer_class = CarSerializer
    queryset = Cars.objects.select_related().all()

    def get(self, request, **kwargs):
        response = self.list(request, **kwargs)
        response.data.append(
            {'token': self._take_new_token()}
        )
        return response

    def post(self, request, **kwargs):
        print(request.data)
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
            print(serialized.validated_data)
            return Response(
                {'token': self._take_new_token()},
                status=status.HTTP_400_BAD_REQUEST
            )


class PutDeleteSegmentAPI(TokenRefresh, DestroyModelMixin, UpdateModelMixin):
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
