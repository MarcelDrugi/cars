import requests
from django.core.signals import request_started
from django.urls import reverse


def before_request(sender, environ, **kwargs):
    if 'HTTP_AUTHORIZATION' in environ and 'HTTP_HOST' in environ:
        url = (
            f"{environ['wsgi.url_scheme']}://{environ['HTTP_HOST']}"
            f"{reverse('refresh_jwt_token')}"
        )
        current_token = environ['HTTP_AUTHORIZATION'][4:]

        json_data = {
            'token': current_token,
        }
        headers = {
            'Content-Type': 'application/json',
        }
        ref_tok_response = requests.post(
            url,
            headers=headers,
            json=json_data,
        ).json()
        if 'token' in ref_tok_response:
            environ['new_token'] = ref_tok_response['token']


request_started.connect(before_request)
