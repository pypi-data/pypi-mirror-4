import json
from weakref import WeakValueDictionary

from requests.compat import urlencode, urljoin
import requests


class Resource(object):
    """
    A descriptor representing a resource endpoint.
    """

    def __init__(self, url):
        self.url = url

    def __get__(self, obj, kls=None):
        if obj is None:
            obj = kls()

        try:
            endpoint = obj._endpoints[self]
        except AttributeError:
            endpoint = ResourceEndpoint(obj, self)
            obj._endpoints = WeakValueDictionary({self: endpoint})
        except KeyError:
            endpoint = ResourceEndpoint(obj, self)
            obj._endpoints[self] = endpoint
        return endpoint


class Endpoint(object):
    def request_args(self):
        args = {}
        if self.api.access_token:
            args['headers'] = {
                'Authorization': 'Bearer %s' % self.api.access_token
            }
        return args

    def get(self, **kwargs):
        request_args = self.request_args()
        r = requests.get(self.url, params=kwargs, **request_args)
        r.raise_for_status()
        response = get_json_response(r)
        if 'objects' in response and 'meta' in response:
            return response['objects']
        else:
            return response


    def post(self, post_data, **kwargs):
        request_args = self.request_args()
        request_args['headers']['Content-type'] = 'application/json'
        json_data = json.dumps(post_data)
        r = requests.post(self.url,
                          data=json_data,
                          params=kwargs,
                          **request_args)
        r.raise_for_status()
        response = get_json_response(r)
        return response


    def __getitem__(self, key):
        return ItemEndpoint(self.api, self.resource, key)


class ItemEndpoint(Endpoint):

    def __init__(self, api, resource, item_id):
        self.api = api
        self.resource = resource
        self.item_id = item_id

    @property
    def url(self):
        resource_url = urljoin(self.resource.url,
                               '%s/' % self.item_id)
        return urljoin(self.api.base_url, resource_url)


class ResourceEndpoint(Endpoint):
    def __init__(self, api, resource):
        self.api = api
        self.resource = resource

    @property
    def url(self):
        return urljoin(self.api.base_url, self.resource.url)


class RestApi(object):
    """
    API session.
    """

    def __init__(self,
                 client_id=None, client_secret=None,
                 access_token=None, refresh_token=None):
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = access_token
        self.refresh_token = refresh_token

    def get_token(self, grant_type, **kwargs):
        url = self.token_url
        form = dict(kwargs,
                    grant_type=grant_type
                    )
        r = requests.post(
            url,
            data=form,
            headers={
                'Accept': 'application/json',
            },
            auth=(self.client_id, self.client_secret),
        )
        r.raise_for_status()

        r_json = get_json_response(r)

        if not r_json:
            raise RestApiError(
                'Token endpoint did not return a valid JSON object'
            )

        try:
            self.access_token = r_json['access_token']
        except KeyError:
            raise RestApiError(
                'Token endpoint did not return an access_token'
            )

        try:
            self.refresh_token = r_json['refresh_token']
        except KeyError:
            pass

    def dialog(self, redirect_uri, scope=(), state='', implicit=False):
        if implicit:
            response_type = 'token'
        else:
            response_type = 'code'

        params = dict(
            response_type=response_type,
            client_id=self.client_id,
            redirect_uri=redirect_uri,
            scope=' '.join(scope),
            state=state,
        )
        return "%s?%s" % (self.dialog_url, urlencode(params))

    def token_auth_code(self, code, redirect_uri):
        return self.get_token('authorization_code',
                              code=code,
                              redirect_uri=redirect_uri,
                              client_id=self.client_id,
        )

    def token_client_credentials(self):
        return self.get_token('client_credentials')

    def token_password(self, username, password, scope=('post_metag',)):
        return self.get_token('password',
                              username=username,
                              password=password,
                              scope=' '.join(scope),
        )

    def resource(self, uri):
        endpoint = Endpoint()
        endpoint.api = self
        endpoint.url = urljoin(self.base_url, uri)
        return endpoint


class RestApiError(Exception):
    pass


def get_json_response(r):
    # requests < 1.0 compatibility hack
    if callable(r.json):
        # requests >= 1.0
        return r.json()
    else:
        # older requests
        return r.json
