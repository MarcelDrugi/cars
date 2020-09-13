"""
Backend API documentation on '/swagger or '/redoc'
"""
from os.path import abspath, dirname, join

import environ
from django.contrib.auth.models import Permission, User
from django.urls import reverse
from django.views.generic import TemplateView
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.generics import CreateAPIView, GenericAPIView
from rest_framework.mixins import (CreateModelMixin, DestroyModelMixin,
                                   ListModelMixin, UpdateModelMixin)
from rest_framework.permissions import (AllowAny, IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response

from paypal.payment_prepare import PaymentLinkGenerator

from .models import Cars, Clients, Discounts, Reservations, Segments
from .permissions import (ClientFullPermissions, ClientGetPermissions,
                          EmployeeGetPermissions)
from .serializers import (AvatarSerializer, CarSerializer,
                          CheckReservationSerializer, ClientSerializer,
                          CreateCarSerializer, DiscountSerializer,
                          MajorOrderDataSerializer, ReservationSerializer,
                          SegmentSerializer, UpdateClientDataSerializer)


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


class ClientsAPI(TokenRefresh, ListModelMixin):
    """
    Handles :model:`car_rental:Clients` for GET requests.
    """
    permission_classes = (IsAuthenticated, )
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


class ClientDataAPI(TokenRefresh, UpdateModelMixin):
    """
    Handles :model:`car_rental:Clients` GET/PATCH requests.
    Serializes and sends the client-acc data after login.
    Patch client-acc data after profile edition.
    """

    queryset = Clients.objects.prefetch_related().all()
    serializer_class = UpdateClientDataSerializer

    def get(self, request, **kwargs):
        try:
            client = self.queryset.get(user__username=kwargs['username'])
        except Clients.DoesNotExist:
            return Response(
                {'error': 'User does not exist'},
                status=status.HTTP_400_BAD_REQUEST
            )
        else:
            avatar_serializer = AvatarSerializer({'avatar': client.avatar})
            serialized_client = ClientSerializer(client)
            return Response(
                {
                    'token': self._take_new_token(),
                    'avatar': avatar_serializer.data,
                    'client': serialized_client.data,
                },
                status=status.HTTP_200_OK
            )

    def patch(self, request, *args, **kwargs):
        if 'new_password' in request.data and 'old_password' in request.data:
            client = self.queryset.get(id=kwargs['pk'])
            user = client.user
            if user.check_password(request.data['old_password']):
                try:
                    user.set_password(request.data['new_password'])
                    user.save()
                except (AttributeError, TypeError):
                    # no new password in request data (or wrong type/format)
                    return Response(status=status.HTTP_400_BAD_REQUEST)
                else:
                    return Response(
                        {'token': self._take_new_token()},
                        status=status.HTTP_200_OK
                    )
            else:
                return Response(
                    {'error': 'Old password is incorrect'},
                    status=status.HTTP_409_CONFLICT
                )
        else:
            response = self.update(request, *args, **kwargs)
            response.data['token'] = self._take_new_token()
            return response


class DiscountsAPI(TokenRefresh, ListModelMixin, CreateModelMixin,
                   DestroyModelMixin):
    """
    Handles :model:`car_rental:Discounts` for GET/PUT/POST requests.
    GET and POST work os standard.
    For PUT request, view doesnt serialize data, but only checks if objects
    exists and merge them (many-to-many relation)
    """
    permission_classes = (EmployeeGetPermissions, IsAuthenticated, )
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
        except (Clients.DoesNotExist, Discounts.DoesNotExist):
            return Response(
                {
                    'token': self._take_new_token(),
                    'error': 'Wrong client/discount id'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        else:
            if request.data['acction'] == 'add':
                client.discount.add(discount)
                client.save()
            else:
                client.discount.remove(discount)
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
    permission_classes = (EmployeeGetPermissions, )

    def get(self, request, **kwargs):
        response = self.list(request, **kwargs)
        response.data.append(
            {'token': self._take_new_token()}
        )
        return response

    def post(self, request, **kwargs):
        serializer = CreateCarSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(raise_exception=True)
            return Response(
                {'token': self._take_new_token()},
                status=status.HTTP_201_CREATED
            )
        else:
            return Response(
                {**serializer.errors, **{'token': self._take_new_token()}},
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

        serializer = CreateCarSerializer(instance=instance, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {'token': self._take_new_token()},
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                {**serializer.errors, **{'token': self._take_new_token()}},
                status=status.HTTP_400_BAD_REQUEST
            )

    def delete(self, request, *args, **kwargs):
        self.destroy(request, *args, **kwargs)
        return Response(
            {'token': self._take_new_token()},
            status=status.HTTP_200_OK
        )


class SegmentsAPI(TokenRefresh, ListModelMixin, DestroyModelMixin,
                  UpdateModelMixin):
    """
    Handles :model:`car_rental:Segments` and the assigned
    :model:`car_rental.PriceLists` for GET/POST/PUT/DELETE requests.
    """

    serializer_class = SegmentSerializer
    queryset = Segments.objects.select_related().all()
    permission_classes = (EmployeeGetPermissions, )

    def get(self, request, **kwargs):
        response = self.list(request, **kwargs)
        response.data.append(
            {'token': self._take_new_token()}
        )
        return response

    def post(self, request, **kwargs):
        serializer = SegmentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()

            return Response(
                {'token': self._take_new_token()},
                status=status.HTTP_201_CREATED
            )
        else:
            return Response(
                {**serializer.errors, **{'token': self._take_new_token()}},
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
        except Segments.DoesNotExist:
            return Response(
                {'error': 'Segment does not exist'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        else:
            segment_serializer = SegmentSerializer(segment)
            return Response(
                {
                    'token': self._take_new_token(),
                    'segment': segment_serializer.data,
                },
                status=status.HTTP_200_OK,
            )


class CheckReservationAPI(TokenRefresh):
    """
    Handles :model:`car_rental:Reservations` for GET/POST request.
    If serializer has parameter `permanent` equal to False, the view
    doesnt create object. Check availability only.
    View only for authenticated users.
    """
    permission_classes = (ClientFullPermissions, IsAuthenticated, )

    def post(self, request, *args, **kwargs):
        serializer_check = CheckReservationSerializer(
            data=request.data,
            permanent=False
        )
        if serializer_check.is_valid():
            try:
                reservation = serializer_check.save()
                serialized_reservation = ReservationSerializer(reservation)
            except ValidationError:
                return Response(status=status.HTTP_409_CONFLICT)
            except AttributeError:
                return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            else:
                try:
                    client = Clients.objects.get(
                        user__username=request.user.username
                    )
                    serialized_client = ClientSerializer(client)
                except Clients.DoesNotExist:
                    # If the user has passed authentication but cannot be found
                    # in the database, this is a dependency error.
                    return Response(status=status.HTTP_424_FAILED_DEPENDENCY)
                return Response(
                    {
                        'token': self._take_new_token(),
                        'reservation': serialized_reservation.data,
                        'client': serialized_client.data,
                     },
                    status=status.HTTP_201_CREATED
                )
        else:
            return Response(
                serializer_check.errors,
                status=status.HTTP_400_BAD_REQUEST
            )


class TermsAPI(TokenRefresh, ListModelMixin):
    permission_classes = ()
    serializer_class = CheckReservationSerializer

    def get_queryset(self):
        if 'car_id' in self.kwargs:
            return Reservations.objects.select_related().filter(
                car__id=self.kwargs['car_id']
            )

    def get(self, request, **kwargs):
        response = self.list(request, **kwargs)
        response.data.append(
            {'token': self._take_new_token()}
        )
        return response


class ReservationAPI(TokenRefresh, DestroyModelMixin, ):
    """
    Handles :model:`car_rental:Reservations` for GET/DELETE requests.
    View only for authenticated users.
    """
    permission_classes = (ClientFullPermissions, IsAuthenticated, )
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


class ClientReservationAPI(TokenRefresh, ListModelMixin):
    serializer_class = ReservationSerializer
    permission_classes = (ClientFullPermissions, IsAuthenticated, )

    def get_queryset(self):
        return Reservations.objects.select_related().filter(
            order__client__user=self.request.user,
        )

    def get(self, request, **kwargs):
        response = self.list(request, **kwargs)
        response.data.append(
            {'token': self._take_new_token()}
        )
        return response


class OrderAPI(TokenRefresh):
    permission_classes = (ClientFullPermissions, IsAuthenticated, )

    def _get_payment_link(self, reservation):
        env = environ.Env()
        env.read_env(
            join(dirname(dirname(abspath(__file__))), '/config/setting/.env')
        )

        success_url = self.request.build_absolute_uri(reverse('paid'))
        cancel_url = self.request.build_absolute_uri(reverse('cancel'))
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
        return paypal.payment(data)

    def post(self, request, *args, **kwargs):
        major_data_serializer = MajorOrderDataSerializer(data=request.data)

        if major_data_serializer.is_valid():
            try:
                reservation = major_data_serializer.save()
            except ValidationError:
                return Response(
                    {'error': 'Car or discount not exist'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            except (TypeError, AttributeError):
                return Response(
                    {'error': 'Wrong data type/format'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        else:
            return Response(
                major_data_serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        paypal_response = self._get_payment_link(reservation)

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
            status=status.HTTP_406_NOT_ACCEPTABLE,
        )

    def get(self, *args, **kwargs):
        try:
            reservation = Reservations.objects.get(id=kwargs['pk'])
        except (AttributeError, Reservations.DoesNotExist):
            return Response(status=status.HTTP_400_BAD_REQUEST)
        paypal_response = self._get_payment_link(reservation)
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
        else:
            return Response(
                status=status.HTTP_406_NOT_ACCEPTABLE,
            )


class SignUp(CreateAPIView):
    """
    Handles :model:`car_rental.Client` and the assigned :model:`auth.User`.
    Contains only one request: POST.
    """
    permission_classes = ()

    def create(self, request, **kwargs):
        avatar = request.data['avatar']
        if avatar == 'undefined':
            data = {'user': request.data}
        else:
            data = {'user': request.data, 'avatar': avatar}
        serializer = ClientSerializer(data=data)

        if serializer.is_valid():
            try:
                serializer.save()
                return Response(
                    serializer.data,
                    status=status.HTTP_201_CREATED
                )
            except User.DoesNotExist:
                return Response(
                    serializer.errors,
                    status=status.HTTP_507_INSUFFICIENT_STORAGE
                )
            except Exception:
                return Response(
                    serializer.errors,
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        else:
            if User.objects.filter(username=request.data['username']).exists():
                return Response(
                    serializer.errors,
                    status=status.HTTP_409_CONFLICT
                )
            else:
                return Response(
                    serializer.errors,
                    status=status.HTTP_400_BAD_REQUEST
                )
