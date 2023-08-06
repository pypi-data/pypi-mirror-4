
class BaseCoder(object):
    def encode(self, data):
        raise NotImplementedError

    def decode(self, data):
        raise NotImplementedError

class BlankCoder(object):
    def encode(self, data):
        return {}

    def decode(self, data):
        return {}
