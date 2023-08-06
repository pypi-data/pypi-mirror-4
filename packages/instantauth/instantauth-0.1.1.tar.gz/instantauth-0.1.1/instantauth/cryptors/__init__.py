
class BaseCryptor(object):
    def encrypt_global(self, stream, secret_key):
        raise NotImplementedError

    def decrypt_global(self, stream, secret_key):
        raise NotImplementedError

    def encrypt_data(self, data, secret_key, private_key):
        raise NotImplementedError

    def decrypt_data(self, data, secret_key, private_key):
        raise NotImplementedError

class PlainCryptor(BaseCryptor):
    def encrypt_global(self, stream, secret_key):
        return stream

    def decrypt_global(self, stream, secret_key):
        return stream

    def encrypt_data(self, data, secret_key, private_key):
        return data

    def decrypt_data(self, data, secret_key, private_key):
        return data

