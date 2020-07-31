import environ
import requests
from django.http import HttpResponseRedirect
from django.views import View

from car_rental.models import Orders
from paypal.payment_prepare import PaymentLinkGenerator


class PayPalSuccessView(View):

    def get(self, request):
        env = environ.Env()
        env.read_env('../cars/.env')

        token = request.GET['token']
        order = Orders.objects.get(payment_id=token)
        order.paid = True
        return HttpResponseRedirect('http://localhost:4200/success')


class PayPalCancelView(View):
    def get(self, request):
        return HttpResponseRedirect('http://localhost:4200/fail')
