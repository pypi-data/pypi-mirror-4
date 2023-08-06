
class BaseCoder(object):
    derived_context = {}

    def encode(self, data):
        raise NotImplementedError

    def decode(self, data):
        raise NotImplementedError


class ConstantCoder(object):
    def __init__(self, encoded='', decoded={}):
        self.encoded = encoded
        self.decoded = decoded

    def encode(self, data):
        return self.encoded

    def decode(self, data):
        return self.decoded

BlankCoder = ConstantCoder

class PlainCoder(object):
    def encode(self, data):
        return data

    def decode(self, data):
        return data
