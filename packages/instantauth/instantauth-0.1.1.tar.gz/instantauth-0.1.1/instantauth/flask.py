
from __future__ import absolute_import

import flask

from instantauth import Authentication

class FlaskAuthentication(Authentication):
    
    def from_request(self):
        data = flask.request.data
        data = self.session_handler.decode_data(data)
        return self.get_context(data)

