import mock
import unittest
from generic_request_signer.response import Response

class ResponseTests(unittest.TestCase):

    sut_class = Response

    def setUp(self):
        self.raw_response = mock.Mock()
        self.raw_response.code = 500
        self.raw_response.read.return_value = "foobar"
        self.sut = self.sut_class(self.raw_response)
        self.json_loads_patch = mock.patch('json.loads')
        self.json_loads = self.json_loads_patch.start()

    def tearDown(self):
        self.json_loads = self.json_loads_patch.stop()

    def test_init_captures_incoming_response_in_raw_form(self):
        self.assertEqual(self.sut.raw_response, self.raw_response)

    def test_will_store_original_raw_response_as_none_by_default(self):
        self.assertEqual(self.sut.original_raw_response, None)

    def test_status_code_property_returns_raw_response_code(self):
        self.assertEqual(500, self.sut.status_code)

    def test_will_read_in_raw_response_when_original_is_still_none(self):
        self.sut.original_raw_response = None
        result = self.sut.read()
        self.assertEqual(result, "foobar")

    def test_will_return_cached_value_when_original_is_already_set(self):
        self.sut.original_raw_response = "glow"
        result = self.sut.read()
        self.assertEqual(result, "glow")

    def test_json_property_returns_empty_object_when_read_results_in_empty_string(self):
        with mock.patch.object(self.sut, 'read') as read:
            read.return_value = ''
            result = self.sut.json
        self.assertEqual(result, {})

    def test_json_property_invokes_json_loads_when_read_results_in_not_empty_string(self):
        with mock.patch.object(self.sut, 'read') as read:
            read.return_value = 'gotime'
            self.sut.json
        self.json_loads.assert_called_once_with('gotime')

    def test_json_property_returns_json_loads_result_when_read_results_in_not_empty_string(self):
        with mock.patch.object(self.sut, 'read') as read:
            read.return_value = 'gotime'
            result = self.sut.json
        self.assertEqual(result, self.json_loads.return_value)

    def test_is_successful_returns_false_when_status_is_500_based(self):
        self.sut.raw_response.code = 500
        self.assertFalse(self.sut.is_successful)

    def test_is_successful_returns_false_when_status_is_400_based(self):
        self.sut.raw_response.code = 400
        self.assertFalse(self.sut.is_successful)

    def test_is_successful_returns_false_when_status_is_200(self):
        self.sut.raw_response.code = 200
        self.assertTrue(self.sut.is_successful)

    def test_is_successful_returns_false_when_status_is_201(self):
        self.sut.raw_response.code = 201
        self.assertTrue(self.sut.is_successful)

    def test_is_successful_returns_false_when_status_is_206(self):
        self.sut.raw_response.code = 206
        self.assertTrue(self.sut.is_successful)

    def test_is_successful_returns_false_when_status_is_204(self):
        self.sut.raw_response.code = 204
        self.assertTrue(self.sut.is_successful)
