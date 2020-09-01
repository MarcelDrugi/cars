from os.path import join, dirname, abspath
import environ
from django.http import HttpResponseRedirect
from django.views import View
from car_rental.models import Orders


def local_env():
    env = environ.Env()
    env.read_env(
        join(dirname(dirname(abspath(__file__))), 'config/setting/.env')
    )
    return env


class PayPalSuccessView(View):
    def get(self, request):
        env = local_env()
        url = env('FRONTEND_HOST') + 'success'

        token = request.GET['token']
        order = Orders.objects.get(payment_id=token)
        order.paid = True
        order.save()

        return HttpResponseRedirect(url)


class PayPalCancelView(View):
    def get(self, request):
        env = local_env()
        url = env('FRONTEND_HOST') + 'fail'
        return HttpResponseRedirect(url)


def test():
    pass

test()