
import urlparse
from . import BaseCoder

class URLQueryCoder(BaseCoder):
    def encode(self, data):
        # No escape!
        return '&'.join('='.join(str(k), str(v)) for k, v in data.items())

    def decode(self, data):
        return urlparse.parse_qs(data)

class SimpleURLQueryCoder(BaseCoder):
    def encode(self, data):
        # No escape!
        return '&'.join('='.join((str(k), str(v))) for k, v in data.items())

    def decode(self, data):
        data = urlparse.parse_qs(data)
        for key in data:
            data[key] = data[key][0]
        return data