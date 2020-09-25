from car_rental.models import Requests


class TrafficMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        r = Requests.objects.create()
        if 'HTTP_AUTHORIZATION' in request.META:
            r.authorisation = True
            r.save()
        return response
