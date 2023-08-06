
from __future__ import absolute_import

import json
from . import BaseCoder

class JsonCoder(BaseCoder):
    def encode(self, data):
        return json.dumps(data, separators=(',',':')) # compact form

    def decode(self, data):
        return json.loads(data)