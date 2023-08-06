
from __future__ import absolute_import

import flask

from instantauth import Authentication

class FlaskAuthentication(Authentication):
    
    def from_request(self):
        #data = flask.request.data dont' work!!
        length = flask.request.headers.get('content-length', type=int)
        if not length:
            raise ValueError("no data")
        data = flask.request.input_stream.read(length)
        if not data:
            raise ValueError("can't read data")
        data = self.session_handler.decode_data(data)
        return self.get_context(data)

    def from_first_request(self):
        length = flask.request.headers.get('content-length', type=int)
        if not length:
            raise ValueError("no data")
        data = flask.request.input_stream.read(length)
        if not data:
            raise ValueError("can't read data")
        data = self.session_handler.decode_data(data)
        return self.get_first_context(data)
