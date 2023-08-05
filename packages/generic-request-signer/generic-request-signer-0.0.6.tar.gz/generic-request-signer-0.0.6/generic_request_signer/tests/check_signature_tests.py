import mock
import unittest
import base64
from generic_request_signer import constants, check_signature


class CheckSignatureForBinaryTests(unittest.TestCase):

    @mock.patch('generic_request_signer.check_signature.check_signature')
    def test_check_signature_for_binary_invokes_check_signature_with_hash_of_binary(self, check_signature_mock):
        payload = 'foobar'
        url_path = "/example/post-it/"
        private_key = 'UHJpdmF0ZSBLZXk='
        signature = "AKm9ZGCZPaYRMnLxpFZ8-ulaCIr_wKYAruZVm36uv3Q="
        expected_payload = {'binary_data':'3858f62230ac3c915f300c664312c63f'}
        check_signature.check_signature_for_binary(signature, private_key, url_path, payload)
        check_signature_mock.assert_called_once_with(signature, private_key, url_path, expected_payload)

class CheckSignatureTests(unittest.TestCase):

    def setUp(self):
        self.TEST_PRIVATE_KEY = 'UHJpdmF0ZSBLZXk='
        self.url_one = "/example/get-it/?q=find"
        self.url_two = "/example/post-it/"
        self.url_post_data = {'q': 'update'}

        # valid signatures for urls above and data
        self.signature_one = "T-lT3uT2wpUobJvDkXpxtsEAl7KmrEg6k3So_Varya8="
        self.signature_two = "AKm9ZGCZPaYRMnLxpFZ8-ulaCIr_wKYAruZVm36uv3Q="

    def test_returns_true_when_private_key_built_from_base64_url_encoded_string(self):
        base64_private_key = base64.urlsafe_b64encode('Private Key')
        signature_valid = check_signature.check_signature(self.signature_one, base64_private_key, self.url_one, None)
        self.assertEqual(True, signature_valid)

    def test_returns_true_when_signatures_match_and_no_post_data(self):
        signature_valid = check_signature.check_signature(self.signature_one, self.TEST_PRIVATE_KEY, self.url_one, None)
        self.assertEqual(True, signature_valid)

    def test_returns_true_when_signatures_match_and_has_post_data(self):
        signature_valid = check_signature.check_signature(self.signature_two, self.TEST_PRIVATE_KEY, self.url_two, self.url_post_data)
        self.assertEqual(True, signature_valid)

    def test_returns_false_when_signatures_dont_match(self):
        bad_signature = "ABCc0hS02rVC3016krevud1aW9B6Ls0Tp4_XcezuXYZ="
        signature_valid = check_signature.check_signature(bad_signature, self.TEST_PRIVATE_KEY, self.url_one, None)
        self.assertEqual(False, signature_valid)

    def test_doesnt_use_signature_already_in_url_to_check_for_valid_signature(self):
        url_with_sig = "{url}&{signature_param}={signature}".format(
            url=self.url_one,
            signature_param=constants.SIGNATURE_PARAM_NAME,
            signature=self.signature_one,
        )

        signature_valid = check_signature.check_signature(self.signature_one, self.TEST_PRIVATE_KEY, url_with_sig, None)
        self.assertEqual(True, signature_valid)

    def test_doesnt_use_signature_already_in_url_to_check_for_valid_signature_with_post_data(self):
        url_with_sig = "{url}?{signature_param}={signature}".format(
            url=self.url_two,
            signature_param=constants.SIGNATURE_PARAM_NAME,
            signature=self.signature_two,
        )

        signature_valid = check_signature.check_signature(self.signature_two, self.TEST_PRIVATE_KEY, url_with_sig, self.url_post_data)
        self.assertEqual(True, signature_valid)


class StripSignatureFromUrlTests(unittest.TestCase):

    def test_strip_signature_from_query_string_after_amp(self):
        url_path = '/api/CheckAuthentication/?__client_id=config&username=None&token=None&__signature=eWDBUhizESZkHtnyE807XbwdvivZKAIfwRltzcuOqgY='
        signature = 'eWDBUhizESZkHtnyE807XbwdvivZKAIfwRltzcuOqgY='
        result = check_signature._strip_signature_from_url(signature, url_path)
        clean_url = '/api/CheckAuthentication/?__client_id=config&username=None&token=None'
        self.assertEqual(result, clean_url)

    def test_strip_signature_from_query_string_with_no_amp(self):
        url_path = '/api/CheckAuthentication/?__signature=eWDBUhizESZkHtnyE807XbwdvivZKAIfwRltzcuOqgY='
        signature = 'eWDBUhizESZkHtnyE807XbwdvivZKAIfwRltzcuOqgY='
        result = check_signature._strip_signature_from_url(signature, url_path)
        self.assertEqual(result, '/api/CheckAuthentication/')


class ConstantTimeCompareTests(unittest.TestCase):

    def test_constant_time_compare(self):
    # It's hard to test for constant time, just test the result.
        self.assertTrue(check_signature.constant_time_compare(b'spam', b'spam'))
        self.assertFalse(check_signature.constant_time_compare(b'spam', b'eggs'))
        self.assertTrue(check_signature.constant_time_compare('spam', 'spam'))
        self.assertFalse(check_signature.constant_time_compare('spam', 'eggs'))
