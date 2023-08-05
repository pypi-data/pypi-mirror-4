from cStringIO import StringIO
import mock
import unittest
from urllib import urlencode
from collections import OrderedDict
from generic_request_signer import constants
from generic_request_signer.factory import SignedRequestFactory, json_encoding, default_encoding

class SignedRequestFactoryTests(unittest.TestCase):

    sut_class = SignedRequestFactory

    def setUp(self):
        self.method = 'GET'
        self.private_key = '1234'
        self.client_id = 'foobar'
        self.raw_data = {'some':'data'}
        self.sut = self.sut_class(self.method, self.client_id, self.private_key, self.raw_data)

    def test_init_captures_incoming_client_id(self):
        self.assertEqual(self.sut.client_id, self.client_id)

    def test_init_captures_incoming_http_method(self):
        self.assertEqual(self.sut.http_method, self.method)

    def test_init_captures_incoming_private_key(self):
        self.assertEqual(self.sut.private_key, self.private_key)

    def test_has_basic_boundary_defined(self):
        self.assertEqual(self.sut.boundary, "----WebKitFormBoundaryJQlIRhP93LbaDnCQ")

    def test_generates_hash_from_binary_data(self):
        attachment = StringIO('some pdf text from a file').read()
        self.sut.http_method = 'POST'
        self.sut.raw_data = {'file': attachment, 'data': {'filename': 'readme.pdf', 'guid': '1234'}}
        result = self.sut._data_or_multiform_post_data()
        self.assertEqual(result, {'binary_data': 'f9f316e8da9f562aec6661cb120fc230'})

    def test_returns_none_when_file_in_data_but_not_post_method(self):
        attachment = StringIO('some pdf text from a file').read()
        self.sut.http_method = 'PUT'
        self.sut.raw_data = {'file': attachment, 'data': {'filename': 'readme.pdf', 'guid': '1234'}}
        result = self.sut._data_or_multiform_post_data()
        self.assertEqual(result, None)

    def test_returns_none_when_post_but_no_file_in_data(self):
        self.sut.http_method = 'POST'
        self.sut.raw_data = {'data': {'filename': 'readme.pdf', 'guid': '1234'}}
        result = self.sut._data_or_multiform_post_data()
        self.assertEqual(result, None)

    @mock.patch('generic_request_signer.factory.file_encoding')
    def test_init_captures_content_type_encodings(self, file_encode):
        with mock.patch('generic_request_signer.factory.json_encoding') as json_encode:
            self.sut = self.sut_class(self.method, self.client_id, self.private_key, self.sut.raw_data)
        self.assertEqual(self.sut.content_type_encodings, {'application/json':json_encode, 'multipart/form-data': file_encode})

    def test_json_encoding_dumps_json_data(self):
        result = json_encoding(['foo', {'bar': ('baz', None, 1.0, 2)}])
        self.assertEqual(result, '["foo", {"bar": ["baz", null, 1.0, 2]}]')

    def test_default_encoding_encodes_url_data(self):
        result = default_encoding({'foo':'bar', 'baz':'broken'})
        self.assertEqual(result, 'foo=bar&baz=broken')

    @mock.patch('apysigner.get_signature')
    def test_build_signed_url_for_get_request_returns_url_with_data_client_id_and_signature(self, get_signature):
        get_signature.return_value = 'zzz123'
        self.sut.raw_data = {'username': u'some.user', 'token': u'813bc1ad91dfadsfsdfsd02c'}
        url = 'http://bit.ly/'
        self.sut.http_method = 'GET'
        self.sut.client_id = 'foobar'
        result = self.sut.build_request_url(url)
        self.assertEqual(result, 'http://bit.ly/?__client_id=foobar&username=some.user&token=813bc1ad91dfadsfsdfsd02c&__signature=zzz123')

    @mock.patch('apysigner.get_signature')
    def test_build_signed_url_for_post_request_returns_url_with_only_client_id_and_signature(self, get_signature):
        get_signature.return_value = 'zzz123'
        self.sut.raw_data = {'username': u'some.user', 'token': u'813bc1ad91dfadsfsdfsd02c'}
        url = 'http://bit.ly/'
        self.sut.http_method = 'POST'
        self.sut.client_id = 'foobar'
        result = self.sut.build_request_url(url)
        self.assertEqual(result, 'http://bit.ly/?__client_id=foobar&__signature=zzz123')

    @mock.patch('apysigner.get_signature')
    def test_build_signed_url_for_get_request_without_raw_data_returns_url_with_only_client_id_and_signature(self, get_signature):
        get_signature.return_value = 'zzz123'
        self.sut.raw_data = None
        url = 'http://bit.ly/'
        self.sut.http_method = 'GET'
        self.sut.client_id = 'foobar'
        result = self.sut.build_request_url(url)
        self.assertEqual(result, 'http://bit.ly/?__client_id=foobar&__signature=zzz123')

    @mock.patch('apysigner.get_signature')
    def test_build_signed_url_invokes_get_signature_with_no_data_when_get_request_and_valid_data(self, get_signature):
        url = 'http://bit.ly/'
        self.sut.raw_data = {'some':'data'}
        self.sut.http_method = 'GET'
        self.sut._build_signed_url(url)
        get_signature.assert_called_once_with(self.private_key, url, {})

    @mock.patch('apysigner.get_signature')
    def test_build_signed_url_invokes_get_signature_with_data_input_when_get_request_but_invalid_data(self, get_signature):
        url = 'http://bit.ly/'
        self.sut.raw_data = None
        self.sut.http_method = 'GET'
        self.sut._build_signed_url(url)
        get_signature.assert_called_once_with(self.private_key, url, None)

    @mock.patch('apysigner.get_signature')
    def test_build_signed_url_invokes_get_signature_with_raw_data_when_post_request(self, get_signature):
        url = 'http://bit.ly/'
        self.sut.http_method = 'POST'
        self.sut._build_signed_url(url)
        get_signature.assert_called_once_with(self.private_key, url, self.sut.raw_data)

    def test_will_modify_the_headers_content_type_to_include_boundary_when_multipart(self):
        self.sut.http_method = 'POST'
        self.sut.raw_data = {'file':''}
        headers = {'Content-Type':'multipart/form-data'}
        self.sut.modify_headers_when_multipart(headers)
        self.assertEqual('multipart/form-data; boundary={}'.format(self.sut.boundary), headers['Content-Type'])

    def test_will_not_modify_the_headers_content_type_when_http_method_is_not_post(self):
        self.sut.http_method = 'PUT'
        self.sut.raw_data = {'file':''}
        headers = {'Content-Type':'multipart/form-data'}
        self.sut.modify_headers_when_multipart(headers)
        self.assertEqual('multipart/form-data', headers['Content-Type'])

    def test_will_not_modify_the_headers_content_type_when_raw_data_has_no_file(self):
        self.sut.http_method = 'POST'
        self.sut.raw_data = {'no_binary_data_here':''}
        headers = {'Content-Type':'multipart/form-data'}
        self.sut.modify_headers_when_multipart(headers)
        self.assertEqual('multipart/form-data', headers['Content-Type'])

    def test_invokes_modify_headers_when_multipart_with_request_headers(self):
        self.sut.raw_data = {'file': 'foo', 'data': {'filename': 'readme.pdf', 'guid': '1234'}}
        headers = {'Content-Type':'multipart/form-data'}
        self.sut.http_method = 'POST'
        with mock.patch.object(self.sut, 'modify_headers_when_multipart') as modify_headers:
            self.sut._get_data_payload(headers)
        modify_headers.assert_called_once_with(headers)

    @mock.patch('generic_request_signer.factory.default_encoding')
    def test_get_data_payload_invokes_get_on_internal_payload_when_raw_data_exists_and_not_get_request(self, default_encoding):
        headers = {'Content-Type':'application/json'}
        self.sut.http_method = 'POST'
        with mock.patch.object(self.sut, 'content_type_encodings') as encodings:
            self.sut._get_data_payload(headers)
        encodings.get.assert_called_once_with('application/json', default_encoding)

    @mock.patch('generic_request_signer.factory.default_encoding')
    def test_get_data_payload_constructs_func_with_raw_data_when_raw_data_exists_and_not_get_request(self, default_encoding):
        headers = {'Content-Type':'application/json'}
        self.sut.http_method = 'POST'
        with mock.patch.object(self.sut, 'content_type_encodings') as encodings:
            self.sut._get_data_payload(headers)
        encodings.get().assert_called_once_with(self.sut.raw_data, self.sut.boundary)

    @mock.patch('generic_request_signer.factory.default_encoding')
    def test_get_data_payload_returns_encoding_func_when_raw_data_exists_and_not_get_request(self, default_encoding):
        headers = {'Content-Type':'application/json'}
        self.sut.http_method = 'POST'
        with mock.patch.object(self.sut, 'content_type_encodings') as encodings:
            result = self.sut._get_data_payload(headers)
        self.assertEqual(result, encodings.get().return_value)

    @mock.patch('generic_request_signer.factory.default_encoding')
    def test_get_data_payload_does_not_invoke_get_on_internal_payload_when_no_raw_data_exists(self, default_encoding):
        self.sut.raw_data = None
        headers = {'Content-Type':'application/json'}
        self.sut.http_method = 'POST'
        with mock.patch.object(self.sut, 'content_type_encodings') as encodings:
            self.sut._get_data_payload(headers)
        self.assertFalse(encodings.get.called)

    @mock.patch('generic_request_signer.factory.default_encoding')
    def test_get_data_payload_returns_none_when_no_raw_data_exists(self, default_encoding):
        self.sut.raw_data = None
        headers = {'Content-Type':'application/json'}
        self.sut.http_method = 'POST'
        with mock.patch.object(self.sut, 'content_type_encodings'):
            result = self.sut._get_data_payload(headers)
        self.assertEqual(result, None)

    @mock.patch('generic_request_signer.factory.default_encoding')
    def test_get_data_payload_does_not_invoke_get_on_internal_payload_when_http_get(self, default_encoding):
        headers = {'Content-Type':'application/json'}
        self.sut.http_method = 'GET'
        with mock.patch.object(self.sut, 'content_type_encodings') as encodings:
            self.sut._get_data_payload(headers)
        self.assertFalse(encodings.get.called)

    @mock.patch('generic_request_signer.factory.default_encoding')
    def test_get_data_payload_returns_none_when_http_get(self, default_encoding):
        headers = {'Content-Type':'application/json'}
        self.sut.http_method = 'GET'
        with mock.patch.object(self.sut, 'content_type_encodings'):
            result = self.sut._get_data_payload(headers)
        self.assertEqual(result, None)

    def test_encodes_dict_of_data(self):
        result = default_encoding(OrderedDict((('a', 1), ('b', 2), ('c', 'asdf'))))
        self.assertEqual('a=1&b=2&c=asdf', result)

    def test_encodes_dict_with_nested_list(self):
        result = default_encoding(OrderedDict((('a', 1), ('b', [2, 4]), ('c', 'asdf'))))
        self.assertEqual('a=1&b=2&b=4&c=asdf', result)

    def test_encodes_dict_with_nested_empty_list(self):
        result = default_encoding(OrderedDict((('a', 1), ('b', []), ('c', 'asdf'))))
        self.assertEqual('a=1&c=asdf', result)

    @mock.patch('generic_request_signer.request.Request', mock.Mock)
    @mock.patch('generic_request_signer.factory.SignedRequestFactory._get_data_payload', mock.Mock)
    @mock.patch('generic_request_signer.factory.SignedRequestFactory.build_request_url')
    def test_create_request_invokes_build_request_url_with_params(self, build_url):
        url = '/foo/'
        self.sut.create_request(url)
        build_url.assert_called_once_with(url)

    @mock.patch('generic_request_signer.request.Request', mock.Mock)
    @mock.patch('generic_request_signer.factory.SignedRequestFactory.build_request_url', mock.Mock)
    @mock.patch('generic_request_signer.factory.SignedRequestFactory._get_data_payload')
    def test_create_request_invokes_get_data_payload_with_params(self, get_payload):
        kwargs = {'headers':'foo'}
        self.sut.create_request('/foo/', **kwargs)
        get_payload.assert_called_once_with(kwargs.get('headers', {}))

    @mock.patch('generic_request_signer.request.Request')
    @mock.patch('generic_request_signer.factory.SignedRequestFactory._get_data_payload')
    @mock.patch('generic_request_signer.factory.SignedRequestFactory.build_request_url')
    def test_create_request_build_actual_request_object_with_params(self, build_url, get_payload, request):
        url = '/foo/'
        args = {'random':'stuff'}
        kwargs = {'headers':'foo'}
        self.sut.http_method = 'GET'
        self.sut.create_request(url, *args, **kwargs)
        request.assert_called_once_with('GET', build_url.return_value, get_payload.return_value, *args, **kwargs)

    @mock.patch('generic_request_signer.factory.SignedRequestFactory._get_data_payload', mock.Mock)
    @mock.patch('generic_request_signer.factory.SignedRequestFactory.build_request_url', mock.Mock)
    @mock.patch('generic_request_signer.request.Request')
    def test_create_request_returns_request_object(self, request):
        result = self.sut.create_request('/foo/', {})
        self.assertEqual(result, request.return_value)

class LegacySignedRequestFactoryTests(unittest.TestCase):

    def setUp(self):
        self.client_id = 'client_id'
        self.private_key = 'oVB_b3qrP3R6IDApALqehQzFy3DpMfob6Y4627WEK5A='
        self.raw_data = {'some':'data'}
        self.sut = SignedRequestFactory('GET', self.client_id, self.private_key, self.raw_data)

    def test_sets_client_id_in_init(self):
        self.assertEqual(self.client_id, self.sut.client_id)

    def test_sets_private_key_in_init(self):
        self.assertEqual(self.private_key, self.sut.private_key)

    def test_adds_client_id_to_url(self):
        url = 'http://example.com/my/url'
        self.sut.raw_data = {}
        request = self.sut.create_request(url)

        querystring = "?{}={}".format(constants.CLIENT_ID_PARAM_NAME, self.client_id)
        querystring += "&{}={}".format(constants.SIGNATURE_PARAM_NAME, 'N1WOdyaBUVlPjKVyL3ionapOLAasFdvagfotfCdCW-Y=')
        self.assertEqual(url + querystring, request.get_full_url())

    def test_adds_signature_to_url(self):
        url = 'http://example.com/my/url'
        self.sut.raw_data = {}
        request = self.sut.create_request(url)

        querystring = "?{}={}".format(constants.CLIENT_ID_PARAM_NAME, self.client_id)
        querystring += "&{}={}".format(constants.SIGNATURE_PARAM_NAME, 'N1WOdyaBUVlPjKVyL3ionapOLAasFdvagfotfCdCW-Y=')
        self.assertEqual(url + querystring, request.get_full_url())

    @mock.patch('urllib2.Request.__init__')
    def test_urlencodes_data_as_part_of_url_when_method_is_get(self, urllib2_request):
        self.sut.raw_data = {'some':'da ta', 'goes':'he re'}
        self.sut.create_request('www.myurl.com')
        self.assertEqual(None, urllib2_request.call_args[0][1])
        url = "www.myurl.com?{}={}&some=da+ta&goes=he+re&{}={}".format(
            constants.CLIENT_ID_PARAM_NAME,
            self.client_id,
            constants.SIGNATURE_PARAM_NAME,
            '6dBfb4JhoJIm7FyzktbhFxBFyLBPTmXn-MLkV-RXLng='
        )
        self.assertEqual(url, urllib2_request.call_args[0][0])

    @mock.patch('urllib2.Request.__init__')
    def test_passes_data_to_urllib_request_when_method_is_not_get(self, urllib2_request):
        self.sut.raw_data = {'some': 'da ta', 'goes': 'he re'}
        self.sut.http_method = 'POST'
        self.sut.create_request('www.myurl.com')
        self.assertEqual(urlencode(self.sut.raw_data), urllib2_request.call_args[0][1])
        url = "www.myurl.com?{}={}&{}={}".format(
            constants.CLIENT_ID_PARAM_NAME,
            self.client_id,
            constants.SIGNATURE_PARAM_NAME,
            '3sh6DOlYgbsCGT5rNlY819eFAdfl6Fy9GiyHHgUAwLQ='
        )
        self.assertEqual(url, urllib2_request.call_args[0][0])

    @mock.patch('urllib2.Request.__init__')
    def test_passes_hash_from_binary_to_urllib_request_as_part_of_signature_when_multipart_form_post(self, request):
        attachment = StringIO('some pdf text from a file').read()
        self.sut.raw_data = {'file': attachment, 'data': {'filename': 'readme.pdf', 'guid': '1234'}}
        self.sut.http_method = 'POST'
        self.sut.create_request('www.myurl.com')
        #self.assertEqual(urlencode(self.sut.raw_data), urllib2_request.call_args[0][1])
        url = "www.myurl.com?{}={}&{}={}".format(
            constants.CLIENT_ID_PARAM_NAME,
            self.client_id,
            constants.SIGNATURE_PARAM_NAME,
            'UJ81GLdrVknMqfVgf88YCzGq_VhwWBfhv-sRD74b_O4='
        )
        self.assertEqual(url, request.call_args[0][0])

    def test_payload_is_empty_on_get_request_when_signed(self):
        url = "www.myurl.com?asdf=1234"
        self.sut.raw_data = {'asdf': '1234'}

        first_request = self.sut._build_signed_url(url)
        second_request = self.sut._build_signed_url(url)

        self.assertEqual(first_request, second_request)

    def test_get_data_payload_returns_none_when_no_raw_data(self):
        self.sut.raw_data = None
        payload_data = self.sut._get_data_payload({})
        self.assertEqual(None, payload_data)

    def test_get_data_payload_returns_none_when_get_request(self):
        self.sut.http_method = "GET"
        payload_data = self.sut._get_data_payload({})
        self.assertEqual(None, payload_data)

    def test_get_data_payload_returns_properly_encoded_data_when_content_type_header_present(self):
        encoder = mock.MagicMock()
        self.sut.http_method = "POST"
        self.sut.content_type_encodings = {"application/json": encoder}

        request_headers = {"Content-Type": "application/json"}
        payload_data = self.sut._get_data_payload(request_headers)
        self.assertEqual(encoder.return_value, payload_data)
        encoder.assert_called_once_with(self.sut.raw_data, self.sut.boundary)

    def test_get_data_payload_returns_default_encoded_data_when_no_content_type_header(self):
        self.sut.http_method = "POST"
        with mock.patch('generic_request_signer.factory.default_encoding') as encoder:
            payload_data = self.sut._get_data_payload(self.sut.raw_data)
        self.assertEqual(encoder.return_value, payload_data)
        encoder.assert_called_once_with(self.sut.raw_data, self.sut.boundary)

    def test_create_request_sends_header_data_to_get_data_payload(self):
        request_kwargs = {"headers": {"Content-Type": "application/json"}}
        with mock.patch.object(self.sut, "_get_data_payload") as get_payload:
            self.sut.create_request("/", **request_kwargs)
        get_payload.assert_called_once_with(request_kwargs["headers"])

    def test_create_request_sends_empty_dict_to_get_data_payload_when_no_header(self):
        with mock.patch.object(self.sut, "_get_data_payload") as get_payload:
            self.sut.create_request("/")
        get_payload.assert_called_once_with({})
