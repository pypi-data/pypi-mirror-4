__author__ = 'Alexandr Emelin'

try:
    from urllib.request import urlopen, Request
except ImportError:
    from urllib2 import urlopen, Request

try:
    import urllib.parse as urlparse
except ImportError:
    import urlparse

import six
import zlib
import hmac
import time
import json
import base64


class Client(object):

    def __init__(self, address, project, public_key, secret_key, timeout=2, send_func=None):
        self.address = address
        self.project = project
        self.public_key = public_key
        self.secret_key = secret_key
        self.timeout = timeout
        self.send_func = send_func

    def prepare_url(self):
        return '/'.join([self.address.rstrip('/'), self.project])

    def sign_encoded_data(self, encoded_data):
        sign = hmac.new(six.b(self.secret_key))
        sign.update(six.b(self.project))
        sign.update(encoded_data)
        return sign.hexdigest()

    def create_header_content(self, encoded_data):
        params = {
            "client": "python",
            "timestamp": str(int(time.time())),
            "public_key": self.public_key,
            "sign": self.sign_encoded_data(encoded_data)
        }
        return " ".join(["%s=%s" % (key, value) for key, value in params.items()])

    def prepare_headers(self, encoded_data):
        header_content = self.create_header_content(encoded_data)
        return {
            'X-Centrifuge-Auth': "Centrifuge %s" % header_content
        }

    def encode_data(self, data):
        json_data = json.dumps(data)
        base64_data = base64.b64encode(six.b(json_data))
        compressed_data = zlib.compress(base64_data)
        return compressed_data

    def prepare(self, data):
        assert isinstance(data, list)
        url = self.prepare_url()
        encoded_data = self.encode_data(data)
        headers = self.prepare_headers(encoded_data)
        return url, headers, encoded_data

    def send(self, data):
        if not self.send_func:
            return self._send(*self.prepare(data))
        else:
            return self.send_func(*self.prepare(data))

    def _send(self, url, headers, encoded_data):
        """
        Send a request to a remote web server using HTTP POST.
        """
        req = Request(url, headers=headers)
        try:
            response = urlopen(req, encoded_data, timeout=self.timeout)
        except Exception as e:
            return None, e
        else:
            data = response.read()
            result = json.loads(data.decode('utf-8'))
            return result, None