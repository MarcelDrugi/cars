import requests


class RefreshTokenMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        if 'HTTP_AUTHORIZATION' in request.META:
            url = request.build_absolute_uri('/api-token-refresh/')
            current_token = request.META['HTTP_AUTHORIZATION'][4:]
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
            refreshed_token = ref_tok_response['token']
            print('NOWY TOKEN', refreshed_token)
            if isinstance(response, requests.Response):
                response.data['token'] = refreshed_token
            else:
                response.data['token'] = None
        return response
