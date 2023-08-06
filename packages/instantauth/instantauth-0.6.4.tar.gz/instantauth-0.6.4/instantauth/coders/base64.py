
from __future__ import absolute_import
import base64

from . import BaseCoder

class Base64Coder(BaseCoder):
    def encode(self, data):
        return base64.b64encode(data)

    def decode(self, data):
        return base64.b64decode(data)

