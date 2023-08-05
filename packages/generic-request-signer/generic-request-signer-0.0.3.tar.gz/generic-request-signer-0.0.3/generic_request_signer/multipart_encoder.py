class MultipartEncoder(object):

    def __init__(self, raw_data, boundary):
        self.raw_data = raw_data
        self.boundary = boundary
        self.body = []

    def encode_multipart_formdata(self):
        for k,v in self.raw_data.items():
            self.body.append(self._generate_multipart_post_body(k))
        self.body.append('--{}--\r\n'.format(self.boundary))
        return '\r\n'.join(self.body)

    def _generate_multipart_post_body(self, key):
        if key == 'file':
            return self._create_multipart_body_element(self.raw_data, key)
        else:
            return self._generate_post_data_body(key)

    def _generate_post_data_body(self, key):
        post_data = []
        for k,v in self.raw_data[key].items():
            post_data.append(self._create_multipart_body_element(self.raw_data[key], k))
        return '\r\n'.join(post_data)

    def _create_multipart_body_element(self, data, key):
        boundary = '--{}'.format(self.boundary)
        disposition = self._generate_content_disposition(key)
        value = data[key]
        return "{}\r\n{}\r\n{}\r\n".format(boundary, disposition, value)

    def _generate_content_disposition(self, key):
        disposition = 'Content-Disposition: form-data; name="{}"{}\r\n'
        return disposition.format('file','; filename="file"') if key == 'file' else disposition.format(key,'')