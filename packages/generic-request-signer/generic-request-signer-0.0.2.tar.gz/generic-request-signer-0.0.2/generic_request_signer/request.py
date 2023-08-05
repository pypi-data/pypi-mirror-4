import urllib2
from exceptions import HttpMethodNotAllowed


class Request(urllib2.Request, object):

    http_method_names = ['get', 'post', 'put', 'delete', 'head', 'options', 'trace']

    def __init__(self, http_method, url, data, *args, **kwargs):
        method_lower = http_method.lower()
        if method_lower not in self.http_method_names:
            raise HttpMethodNotAllowed
        self.http_method = http_method
        super(Request, self).__init__(url, data, *args, **kwargs)

    def get_method(self):
        return self.http_method
