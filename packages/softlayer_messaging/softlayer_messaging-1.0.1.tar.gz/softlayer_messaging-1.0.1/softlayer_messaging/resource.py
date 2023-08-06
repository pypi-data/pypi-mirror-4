""" See COPYING for license information """
import requests
from softlayer_messaging.errors import ResponseError
from softlayer_messaging.constants import VERSION


class Resource(object):
    """ HTTP Wrapper """
    def __init__(self, url):
        self.url = url.rstrip('/')
        self.headers = {
            'User-Agent': 'SoftLayer Queue Python v%s' % VERSION
        }

    def __getitem__(self, key):
        return Resource(self.child_path(key))

    def child_path(self, path):
        return "/".join((self.url, path))

    def get(self, *args, **kwargs):
        return self.request('GET', *args, **kwargs)

    def put(self, *args, **kwargs):
        return self.request('PUT', *args, **kwargs)

    def post(self, *args, **kwargs):
        return self.request('POST', *args, **kwargs)

    def delete(self, *args, **kwargs):
        return self.request('DELETE', *args, **kwargs)

    def head(self, *args, **kwargs):
        return self.request('HEAD', *args, **kwargs)

    def request(self, method, path="", **kwargs):
        url = self.url
        if path:
            url = "/".join((self.url, path))
        headers = dict(self.headers)
        if 'headers' in kwargs:
            headers.update(kwargs['headers'])
        kwargs['headers'] = headers
        return Response(requests.request(method, url, **kwargs))

    def __repr__(self):
        return '<Resource [%s]>' % (self.url)


class Response(object):
    def __init__(self, resp):
        self.resp = resp
        self.status_code = self.resp.status_code
        self.url = self.resp.url
        self.headers = self.resp.headers
        self.request = self.resp.request
        self.error = self.resp.error

    def __repr__(self):
        return '<Response [%s]>' % (self.status_code)

    @property
    def content(self):
        return self.resp.content

    @property
    def text(self):
        return self.resp.text

    @property
    def json(self):
        return self.resp.json

    def raise_for_status(self):
        if self.error:
            raise self.error

        if self.status_code >= 400:
            code = self.status_code
            message = "Error"
            errors = None
            response = self.json
            if response:
                message = response.get('message') or message
                errors = response.get('errors')

            raise ResponseError("%s: %s" % (code, message), errors)
