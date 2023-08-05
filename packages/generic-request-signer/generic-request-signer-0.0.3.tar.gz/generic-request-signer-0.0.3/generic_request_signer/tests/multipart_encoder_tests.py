import unittest
from generic_request_signer.multipart_encoder import MultipartEncoder

class MultipartEncoderTests(unittest.TestCase):

    sut_class = MultipartEncoder

    def setUp(self):
        self.boundary = '--foo'
        self.raw_data = {'file': 'binary_value', 'data': {'name': 'readme.pdf', 'guid': '1234'}}
        self.sut = self.sut_class(self.raw_data, self.boundary)

    def test_generate_multipart_post_body_returns_string_with_filename_when_key_is_file(self):
        result = self.sut._generate_multipart_post_body('file')
        expected = '----foo\r\nContent-Disposition: form-data; name="file"; filename="file"\r\n\r\nbinary_value\r\n'
        self.assertEqual(result, expected)

    def test_generate_multipart_post_body_returns_string_without_filename_when_key_is_data(self):
        result = self.sut._generate_multipart_post_body('data')
        expected = '----foo\r\nContent-Disposition: form-data; name="guid"\r\n\r\n1234\r\n\r\n----foo\r\nContent-Disposition: form-data; name="name"\r\n\r\nreadme.pdf\r\n'
        self.assertEqual(result, expected)

    def test_encode_multipart_form_data_returns_formatted_string_with_all_elements_of_multipart_post(self):
        result = self.sut.encode_multipart_formdata()
        expected = '----foo\r\nContent-Disposition: form-data; name="guid"\r\n\r\n1234\r\n\r\n----foo\r\nContent-Disposition: form-data; name="name"\r\n\r\nreadme.pdf\r\n\r\n----foo\r\nContent-Disposition: form-data; name="file"; filename="file"\r\n\r\nbinary_value\r\n\r\n----foo--\r\n'
        self.assertEqual(result, expected)

    def test_create_multipart_body_element_creates_formatted_part_given_data_dictionary_and_key(self):
        result = self.sut._create_multipart_body_element(self.raw_data['data'], 'name')
        expected = '----foo\r\nContent-Disposition: form-data; name="name"\r\n\r\nreadme.pdf\r\n'
        self.assertEqual(result, expected)

    def test_generate_content_disposition_returns_name_of_file_if_key_is_file(self):
        result = self.sut._generate_content_disposition('file')
        expected = 'Content-Disposition: form-data; name="file"; filename="file"\r\n'
        self.assertEqual(result, expected)

    def test_generate_content_disposition_returns_name_of_key_if_key_is_not_file(self):
        result = self.sut._generate_content_disposition('name')
        expected = 'Content-Disposition: form-data; name="name"\r\n'
        self.assertEqual(result, expected)
