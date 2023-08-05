import mock
import unittest
from generic_request_signer.request import Request
from generic_request_signer.exceptions import HttpMethodNotAllowed

class RequestTests(unittest.TestCase):

    sut_class = Request

    def test_urllib2_super_invoked_with_params(self):
        url = '/'
        data = {}
        args = {'some':'args'}
        kwargs = {'more':'kwargs'}
        with mock.patch('urllib2.Request.__init__') as init:
            self.sut_class('GET', url, data, *args, **kwargs)
        init.assert_called_once_with(url, data, *args, **kwargs)

    def test_init_captures_incoming_http_method(self):
        with mock.patch('urllib2.Request.__init__'):
            sut = self.sut_class('GET', '/', {})
        self.assertEqual(sut.http_method, 'GET')

    def test_get_http_method_returns_correct_method(self):
        sut = self.sut_class('GET', '/', {})
        self.assertEqual(sut.get_method(), 'GET')

    def test_will_raise_exception_when_http_method_not_allowed(self):
        with self.assertRaises(HttpMethodNotAllowed):
            self.sut_class('HUH', '/', {})

    def test_will_not_raise_exception_when_http_method_is_allowed(self):
        with self.assertRaises(AssertionError):
            with self.assertRaises(HttpMethodNotAllowed):
                self.sut_class('POST', '/', {})

    def test_has_specific_set_of_http_methods_allowed(self):
        allowed_http_methods = ['get', 'post', 'put', 'delete', 'head', 'options', 'trace']
        self.assertEqual(allowed_http_methods, self.sut_class.http_method_names)
