

class Verifier(object):
    def divide_verifier_data(self, raw_data, secret_key):
        raise NotImplementedError

    def public_key_from_verifier(self, verifier, secret_key):
        raise NotImplementedError

    def verify(self, verifier, private_key, secret_key):
        raise NotImplementedError

    def encode_verifier(self, private_key, public_key, secret_key):
        raise NotImplementedError
    
    def merge_verifier_data(self, verifier, raw_data, secret_key):
        raise NotImplementedError


class BypassVerifier(Verifier):
    def __init__(self, public_key='public_key'):
        self.public_key = public_key

    def divide_verifier_data(self, raw_data, secret_key):
        return '', raw_data

    def public_key_from_verifier(self, verifier, secret_key):
        return self.public_key

    def verify(self, verifier, private_key, secret_key):
        return True

    def encode_verifier(self, private_key, public_key, secret_key):
        return ''
    
    def merge_verifier_data(self, verifier, raw_data, secret_key):
        return raw_data
