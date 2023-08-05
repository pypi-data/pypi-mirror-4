from cStringIO import StringIO
import unittest
from generic_request_signer.factory import MultipartSignedRequestFactory


class MultipartSignedRequestFactoryTests(unittest.TestCase):
    """
    usage example:
    >>> import urllib2
    >>> from generic_request_signer.factory import MultipartSignedRequestFactory
    >>>
    >>> factory = MultipartSignedRequestFactory('POST', 'client_id', 'private_key', {'policy': '9999'})
    >>> urllib2.urlopen(factory.create_multipart_request('url', {'file': ('img.jpeg', file('img.jpeg'))}))
    """

    def test_get_content_type_returns_correct_content_type(self):
        sut = MultipartSignedRequestFactory(None, None, None, None)
        self.assertEqual("Content-Type: image/jpeg", sut.get_content_type("img.jpeg"))
        self.assertEqual("Content-Type: image/jpeg", sut.get_content_type("img.jpg"))
        self.assertEqual("Content-Type: application/pdf", sut.get_content_type("doc.pdf"))
        self.assertEqual("Content-Type: application/msword", sut.get_content_type("doc.doc"))
        self.assertEqual("Content-Type: application/vnd.openxmlformats-officedocument.wordprocessingml.document", sut.get_content_type("doc.docx"))

    def test_flatten_multipart_body_returns_string(self):
        sut = MultipartSignedRequestFactory(None, None, None, None)
        result = sut.flatten_multipart_body((('field1', 'val1'), ('field2', 'val2')))
        self.assertEqual('field1\r\nval1\r\nfield2\r\nval2\r\n--{}--\r\n'.format(sut.boundary), result)

    def test_get_multipart_files_returns_list_of_files(self):
        sut = MultipartSignedRequestFactory(None, None, None, None, files={'file1': ('file1.jpeg', StringIO("f1")), 'file2': ('file2.jpeg', StringIO("f2"))})
        result = sut.get_multipart_files()
        self.assertItemsEqual([[
            sut.part_boundary,
            'Content-Disposition: file; name="file1"; filename="file1.jpeg"',
            'Content-Type: image/jpeg', '', 'f1'
        ], [
            sut.part_boundary,
            'Content-Disposition: file; name="file2"; filename="file2.jpeg"',
            'Content-Type: image/jpeg', '', 'f2'
        ]], result)

    def test_get_multipart_fields_returns_list_of_fields(self):
        sut = MultipartSignedRequestFactory(None, None, None, None)
        result = sut.get_multipart_fields({'field1': 'v1', 'field2': 'v2'})
        self.assertItemsEqual([[
            sut.part_boundary,
            'Content-Disposition: form-data; name="field1"',
            '', 'v1'
        ], [
            sut.part_boundary,
            'Content-Disposition: form-data; name="field2"',
            '', 'v2'
        ]], result)

    def test_get_multipart_body_returns_entire_request_body(self):
        sut = MultipartSignedRequestFactory(None, None, None, None, files={'file': ('file1.jpeg', StringIO("image"))})
        result = sut.get_multipart_body({'field1': 'value1'})
        self.assertEqual('{b}\r\nContent-Disposition: form-data; name="field1"'
                         '\r\n\r\nvalue1\r\n{b}\r\n'
                         'Content-Disposition: file; name="file"; filename="file1.jpeg"\r\n'
                         'Content-Type: image/jpeg\r\n\r\n'
                         'image\r\n{b}--\r\n'.format(b=sut.part_boundary), result)

    def test_build_request_sets_method_url_body_and_header(self):
        sut = MultipartSignedRequestFactory("GET", None, None, None)
        result = sut._build_request("BODY", 'http://localhost')
        self.assertEqual("GET", result.http_method)
        self.assertEqual("http://localhost", result.get_full_url())
        self.assertEqual("BODY", result.data)
        self.assertEqual('multipart/form-data; boundary={}'.format(sut.boundary), result.headers['Content-type'])

    def test_create_multipart_request_returns_request_with_signature(self):
        sut = MultipartSignedRequestFactory("GET", 'client', 'YQ==', data={'data': 'one'}, files={'f1': ('f.jpg', StringIO("f1"))})
        result = sut.create_request('http://localhost/asdf')
        self.assertEqual('http://localhost/asdf?__client_id=client&data=one&__signature=NSTBEfeYJZKsqn-sm8Rtt4PqbPzMbedISAujopMXjfg=', result.get_full_url())
