
"""
Install 'pycrypto' package to use this module
"""

from Crypto.Cipher import AES

from . import BaseCryptor

def add_padding(data, block_size):
    data_len = len(data)
    pad_len = (block_size - data_len) % block_size
    if pad_len == 0:
        pad_len = block_size
    padding = chr(pad_len)
    return ''.join((data, padding * pad_len))

def strip_padding(data):
    padding = data[-1]
    pad_len = ord(padding)
    return data[:-pad_len]

def cut_key(key, block_size):
    while len(key) < block_size: # ...
        key += key
    return key[:block_size]


class AESCryptor(BaseCryptor):
    def __init__(self, bits=128, iv=chr(0) * 16): # iv is useless for temporary data in usual case
        if not bits in (128, 192, 256):
            raise ValueError(bits) # make one
        self.block_size = bits / 8
        self.iv = iv

    def encrypt_global(self, stream, secret_key):
        secret_key = cut_key(secret_key, self.block_size)
        cipher = AES.new(secret_key, AES.MODE_CBC, self.iv)
        padded = add_padding(stream, self.block_size)
        encrypted = cipher.encrypt(padded)
        return encrypted

    def decrypt_global(self, stream, secret_key):
        secret_key = cut_key(secret_key, self.block_size)
        cipher = AES.new(secret_key, AES.MODE_CBC, self.iv)
        decrypted = cipher.decrypt(stream)
        return strip_padding(decrypted)

    def encrypt_data(self, data, secret_key, private_key):
        secret_key = cut_key(private_key, self.block_size)
        cipher = AES.new(secret_key, AES.MODE_CBC, self.iv)
        padded = add_padding(data, self.block_size)
        encrypted = cipher.encrypt(padded)
        return encrypted

    def decrypt_data(self, data, secret_key, private_key):
        secret_key = cut_key(private_key, self.block_size)
        cipher = AES.new(secret_key, AES.MODE_CBC, self.iv)
        decrypted = cipher.decrypt(data)
        return strip_padding(decrypted)
