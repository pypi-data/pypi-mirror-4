import json
import requests
from error import MajorApiError


class MajorApiQuickbooks(object):
    PRODUCTION_API_KEY_LENGTH = 32
    STAGING_API_KEY_LENGTH = 24
    DEVELOPMENT_API_KEY_LENGTH = 16

    urls = {
        'production': 'https://majorapi.com/api/quickbooks/',
        'staging': 'https://staging.majorapi.com/api/quickbooks/',
        'development': 'http://localhost:8000/api/quickbooks/',
    }

    success_codes = [200, 201, 202]

    def __init__(self, application_username, application_api_key):
        self.application_username = application_username.lower()
        self.application_api_key = application_api_key.strip()
        self.base_url = self._determine_url()

    @property
    def base_url(self):
        if not self._base_url:
            raise MajorApiError('No URL is configured. '
                                'Please use a valid API Key.')
        return self._base_url

    @base_url.setter
    def base_url(self, value):
        self._base_url = value

    def create_customer(self, customer):
        return self._send_request('POST', 'customers', customer)

    def create_invoice(self, order):
        order['type'] = 'invoice'
        return self._send_request('POST', 'orders', order)

    def create_sales_order(self, order):
        order['type'] = 'sales-order'
        return self._send_request('POST', 'orders', order)

    def retrieve_invoice(self, ref_number):
        resource = 'orders/%s' % ref_number
        return self._send_request('GET', resource)

    def retrieve_sales_order(self, ref_number):
        resource = 'orders/%s' % ref_number
        return self._send_request('GET', resource)

    def retrieve_customer(self, customer_name):
        resource = 'customers/%s' % customer_name
        return self._send_request('GET', resource)

    def retrieve_item(self, item_name):
        resource = 'items/%s' % item_name
        return self._send_request('GET', resource)

    def _determine_url(self):
        api_key_length = len(self.application_api_key)

        if api_key_length == self.PRODUCTION_API_KEY_LENGTH:
            return self.urls['production']
        elif api_key_length == self.STAGING_API_KEY_LENGTH:
            return self.urls['staging']
        elif api_key_length == self.DEVELOPMENT_API_KEY_LENGTH:
            return self.urls['development']
        else:
            return None

    def _send_request(self, method, resource, data=None):
        url = '%s%s' % (self.base_url, resource)
        auth = (self.application_username, self.application_api_key)

        headers = {
            'Accept': 'application/json',
            'User-Agent': '%s python client' % self.application_username
        }

        response = requests.request(method, url, headers=headers,
                                    data=data, auth=auth, verify=True)

        if response.status_code not in self.success_codes:
            error = json.loads(response.content)['message']
            raise MajorApiError('An error occurred when attempting to contact '
                                'QuickBooks REST API. The error states: %s'
                                % error)

        return json.loads(response.content)
