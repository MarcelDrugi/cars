""" Custom PayPal configuration """
import base64
import json
import requests


class PaymentLinkGenerator:
    """
    The class supports single payments.
    Sends payment details and receives payment-links for the customer.
    """

    # Public links to PayPal REST API
    paypal_gen_token_link = 'https://api.sandbox.paypal.com/v1/oauth2/token'
    paypal_order_link = 'https://api.sandbox.paypal.com/v2/checkout/orders'

    def __init__(self, client_id, client_secret, success_url=None,
                 cancel_url=None):
        self.client_id = client_id
        self.client_secret = client_secret
        self.success_url = success_url
        self.cancel_url = cancel_url

    def _get_token(self):
        """ Generates authorization token """

        url = self.paypal_gen_token_link
        data = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'grant_type': 'client_credentials'
        }
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Authorization': 'Basic {0}'.format(base64.b64encode(
                (self.client_id + ':' + self.client_secret).encode()).decode())
        }

        response = requests.post(url, data, headers=headers)
        token = json.loads(response.content)['access_token']
        return token

    def _tax_calculate(self, amount, rate):
        if not isinstance(amount, float) or not isinstance(rate, float):
            raise TypeError('amount and rate must to be FLOAT')
        tax = round(amount * rate, 2)
        return amount - tax, tax

    def payment(self, payment_data):
        """
        Method sends payment details and receives prepared payment-links
            :param dict payment_data: must contain
                :name str:
                :value float:
                :reg_number str:
        """

        taxation = self._tax_calculate(payment_data['value'], 0.23)

        token = self._get_token()
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + token
        }
        url = self.paypal_order_link

        data = {
            'intent': 'CAPTURE',
            'application_context': {
                'return_url': self.success_url,
                'cancel_url': self.cancel_url,
                'brand_name': 'EXAMPLE INC',
                'landing_page': 'BILLING',
                'user_action': 'CONTINUE'
            },
            'purchase_units': [
                {
                    'description': 'Car Rental',
                    'soft_descriptor': 'Zielona Wypozyczalnia',
                    'amount': {
                        'currency_code': 'PLN',
                        'value': payment_data['value'],
                        'breakdown': {
                            'item_total': {
                                'currency_code': 'PLN',
                                'value': taxation[0]
                            },
                            'tax_total': {
                                'currency_code': 'PLN',
                                'value': taxation[1]
                            },
                        }
                    },
                    'items': [
                        {
                            'name': payment_data['name'],
                            'description': payment_data['reg_number'],
                            'sku': 'sku01',
                            'unit_amount': {
                                'currency_code': 'PLN',
                                'value': taxation[0]
                            },
                            'tax': {
                                'currency_code': 'PLN',
                                'value': taxation[1]
                            },
                            'quantity': '1',
                            'category': 'PHYSICAL_GOODS'
                        },
                    ],
                }
            ]
        }
        resp = requests.post(url, json.dumps(data), headers=headers)
        clean_resp = json.loads(resp.content)
        clean_resp['token'] = token
        return clean_resp

    def check_payment(self):
        token = self._get_token()
        headers = {
            'content-type': 'application/json',
            'authorization': 'Bearer ' + token
        }
        url = 'https://api.sandbox.paypal.com/retail/merchant/v1/status'
        resp = requests.get(url, headers=headers)
        return json.loads(resp.content)
