import json
import request
import constants
import apysigner
from urllib import urlencode
from generic_request_signer.multipart_encoder import MultipartEncoder
from generic_request_signer.check_signature import generate_hash_for_binary

def default_encoding(raw_data, *args):
    return urlencode(raw_data, doseq=True)

def json_encoding(raw_data, *args):
    return json.dumps(raw_data)

def file_encoding(raw_data, *args):
    return MultipartEncoder(raw_data, *args).encode_multipart_formdata()

class SignedRequestFactory(object):

    boundary = "----WebKitFormBoundaryJQlIRhP93LbaDnCQ"

    def __init__(self, http_method, client_id, private_key, data):
        self.client_id = client_id
        self.private_key = private_key
        self.http_method = http_method
        self.raw_data = data
        self.content_type_encodings = {
            'application/json': json_encoding,
            'multipart/form-data': file_encoding,
            }

    def create_request(self, url, *args, **request_kwargs):
        url = self.build_request_url(url)
        data = self._get_data_payload(request_kwargs.get("headers", {}))
        return request.Request(self.http_method, url, data, *args, **request_kwargs)

    def build_request_url(self, url):
        url = self._build_client_url(url)
        if self._is_get_request_with_data():
            url += "&{0}".format(urlencode(self.raw_data))
        return self._build_signed_url(url)

    def _build_signed_url(self, url):
        data = self._get_data_based_on_http_method()
        signature = apysigner.get_signature(self.private_key, url, data)
        signed_url = url + "&{}={}".format(constants.SIGNATURE_PARAM_NAME, signature)
        return signed_url

    def _get_data_payload(self, request_headers):
        if self.raw_data and self.http_method.lower() != 'get':
            encoding_func = self.content_type_encodings.get(request_headers.get("Content-Type"), default_encoding)
            self.modify_headers_when_multipart(request_headers)
            return encoding_func(self.raw_data, self.boundary)

    def modify_headers_when_multipart(self, request_headers):
        if self.is_multipart_http_post:
            new_content_type = "{}; boundary={}".format(request_headers.get("Content-Type"), self.boundary)
            request_headers['Content-Type'] = new_content_type

    def _get_data_based_on_http_method(self):
        data = {} if self._is_get_request_with_data() else self.raw_data
        return self._data_or_multiform_post_data() or data

    def _is_get_request_with_data(self):
        return self.http_method.lower() == 'get' and self.raw_data

    def _data_or_multiform_post_data(self):
        if self.is_multipart_http_post:
            return generate_hash_for_binary(self.raw_data['file'])

    @property
    def is_multipart_http_post(self):
        return self.http_method.lower() == 'post' and 'file' in self.raw_data.keys()

    def _build_client_url(self, url):
        url += "?%s=%s" % (constants.CLIENT_ID_PARAM_NAME, self.client_id)
        return url