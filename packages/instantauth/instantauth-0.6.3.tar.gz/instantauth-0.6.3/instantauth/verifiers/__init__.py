
from collections import namedtuple

DividedData = namedtuple('DividedData', ('verification', 'data'))
DestructedData = namedtuple('DestructedData', ('public_key', 'verification', 'data'))


class Verifier(object):
    derived_context = {}

    def divide_verification_and_data(self, raw_data, secret_key):
        raise NotImplementedError
        return DividedData(None, None) # expected interface

    def public_key_from_verification(self, verification, secret_key):
        raise NotImplementedError

    def destruct_data(self, raw_data, secret_key):
        vnd = self.divide_verification_and_data(raw_data, secret_key)
        public_key = self.public_key_from_verification(vnd.verification, secret_key)
        return DestructedData(public_key, vnd.verification, vnd.data)

    def destruct_first_data(self, raw_data, secret_key):
        return self.destruct_data(raw_data, secret_key)

    def verify(self, destructd, private_key, secret_key):
        raise NotImplementedError

    def encode_verification(self, private_key, public_key, secret_key):
        raise NotImplementedError

    def merge_verification_data(self, verification, raw_data, secret_key):
        raise NotImplementedError

    def construct_data(self, raw_data, private_key, public_key, secret_key):
        verification = self.encode_verification(private_key, public_key, secret_key)
        data = self.merge_verification_data(verification, raw_data, secret_key)
        return data

    def construct_first_data(self, raw_data, session_key, secret_key):
        return self.construct_data(raw_data, secret_key, session_key, secret_key)


class BypassVerifier(Verifier):
    def __init__(self, public_key='public_key'):
        self.public_key = public_key

    def divide_verification_and_data(self, raw_data, secret_key):
        return DividedData(None, raw_data)

    def public_key_from_verification(self, verification, secret_key):
        return self.public_key

    def verify(self, destructed, private_key, secret_key):
        return True

    def encode_verification(self, private_key, public_key, secret_key):
        return None

    def merge_verification_data(self, verification, raw_data, secret_key):
        return raw_data


class DataKeyVerifier(Verifier):
    """Supposed to used with PlainCoder"""
    def __init__(self, coder, key):
        self.coder = coder
        self.key = key

    def destruct_data(self, raw_data, secret_key):
        decoded_data = self.coder.decode(raw_data)
        verification = decoded_data[self.key]
        return DestructedData(verification, verification, decoded_data)

    def verify(self, verification, private_key, secret_key):
        return verification

    def construct_data(self, data, private_key, public_key, secret_key):
        data[self.key] = public_key
        return self.coder.encode(data)
