
class BaseCryptor(object):
    derived_context = {}

    def encrypt_global(self, stream, secret_key):
        raise NotImplementedError

    def decrypt_global(self, stream, secret_key):
        raise NotImplementedError

    def encrypt_data(self, data, private_key, secret_key):
        raise NotImplementedError

    def decrypt_data(self, data, private_key, secret_key):
        raise NotImplementedError

    def decrypt_first_data(self, data, secret_key):
        return self.decrypt_data(data, secret_key, secret_key)

    def encrypt_first_data(self, data, secret_key):
        return self.encrypt_data(data, secret_key, secret_key)

class PlainCryptor(BaseCryptor):
    def encrypt_global(self, stream, secret_key):
        return stream

    def decrypt_global(self, stream, secret_key):
        return stream

    def encrypt_data(self, data, private_key, secret_key):
        return data

    def decrypt_data(self, data, private_key, secret_key):
        return data

