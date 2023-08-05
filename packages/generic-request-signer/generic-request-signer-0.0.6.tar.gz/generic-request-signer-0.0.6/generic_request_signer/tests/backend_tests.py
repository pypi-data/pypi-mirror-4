import mock
import unittest
from generic_request_signer import backend


class BasicSettingsApiCredentialsBackendTests(unittest.TestCase):

    sut_class = backend.BasicSettingsApiCredentialsBackend

    def setUp(self):
        self.client = mock.Mock()
        self.sut = self.sut_class(self.client)

    def test_client_error_message_is_defined(self):
        self.assertEqual(self.sut.CLIENT_ERROR_MESSAGE, "Client implementations must define a `{0}` attribute")

    def test_client_settings_error_message_is_defined(self):
        self.assertEqual(self.sut.CLIENT_SETTINGS_ERROR_MESSAGE, "Settings must contain a `{0}` attribute")

    def test_init_captures_incoming_client(self):
        self.assertEqual(self.sut.client, self.client)

    def test_base_url_invokes_get_setting_with_domain_settings_name(self):
        with mock.patch.object(self.sut_class, 'get_setting') as get_setting:
            self.sut.base_url
        get_setting.assert_called_once_with('domain_settings_name')

    def test_base_url_invokes_get_setting_with_client_id_settings_name(self):
        with mock.patch.object(self.sut_class, 'get_setting') as get_setting:
            self.sut.client_id
        get_setting.assert_called_once_with('client_id_settings_name')

    def test_base_url_invokes_get_setting_with_private_key_settings_name(self):
        with mock.patch.object(self.sut_class, 'get_setting') as get_setting:
            self.sut.private_key
        get_setting.assert_called_once_with('private_key_settings_name')

    def test_get_setting_must_be_implemented(self):
        with self.assertRaises(NotImplementedError):
            self.sut.get_setting('foo')
