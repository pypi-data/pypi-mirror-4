import urllib2
import response
import factory


class Client(object):

    def __init__(self, api_credentials):
        self.api_credentials = api_credentials

    def get_factory(self, files):
        if files:
            return factory.MultipartSignedRequestFactory
        return factory.SignedRequestFactory

    def _get_response(self, http_method, endpoint, data=None, files=None, **request_kwargs):
        try:
            http_response = urllib2.urlopen(self._get_request(http_method, endpoint, data, files, **request_kwargs))
        except urllib2.HTTPError as e:
            http_response = e
        return response.Response(http_response)

    def _get_request(self, http_method, endpoint, data=None, files=None, **request_kwargs):
        factory_class = self.get_factory(files)
        request_factory = factory_class(http_method, self._client_id, self._private_key, data, files)
        service_url = self._get_service_url(endpoint)
        return request_factory.create_request(service_url, **request_kwargs)

    def _get_service_url(self, endpoint):
        return self._base_url + endpoint

    @property
    def _base_url(self):
        return self.api_credentials.base_url

    @property
    def _client_id(self):
        return self.api_credentials.client_id

    @property
    def _private_key(self):
        return self.api_credentials.private_key
