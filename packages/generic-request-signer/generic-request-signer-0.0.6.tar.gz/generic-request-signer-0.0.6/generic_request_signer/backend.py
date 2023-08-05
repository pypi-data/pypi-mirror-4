class BasicSettingsApiCredentialsBackend(object):

    CLIENT_ERROR_MESSAGE = "Client implementations must define a `{0}` attribute"
    CLIENT_SETTINGS_ERROR_MESSAGE = "Settings must contain a `{0}` attribute"

    def __init__(self, client):
        self.client = client

    @property
    def base_url(self):
        return self.get_setting('domain_settings_name')

    @property
    def client_id(self):
        return self.get_setting('client_id_settings_name')

    @property
    def private_key(self):
        return self.get_setting('private_key_settings_name')

    def get_setting(self, name):
        raise NotImplementedError
