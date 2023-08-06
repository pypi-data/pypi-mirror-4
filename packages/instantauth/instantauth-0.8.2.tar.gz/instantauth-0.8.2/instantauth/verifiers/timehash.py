
import time
import hashlib
from . import Verifier, DividedData
from ..exceptions import *

class AuthenticationFormatCorrupted(AuthenticationError):
    pass

class AuthenticationHashInvalid(AuthenticationError):
    pass

class AuthenticationExpired(AuthenticationError):
    pass

def timehash(private_key, public_key, hextime):
    m = hashlib.sha1()
    m.update(private_key)
    m.update(public_key)
    m.update(hextime)
    return m.hexdigest()

class TimeHashVerifier(Verifier):
    def __init__(self, limits=(300, 180), now=time.time):
        self.__pastlimit, self.__futurelimit = limits
        self.now = now

    def divide_verification_and_data(self, raw_data, secret_key):
        try:
            vals = raw_data.split('$', 2) # no rsplit - rightmost value can be bytes
        except ValueError:
            raise AuthenticationFormatCorrupted
        return DividedData(vals[0] + '$' + vals[1], vals[2])

    def public_key_from_verification(self, verification, secret_key):
        try:
            public_key, others = verification.split('$', 1)
        except ValueError:
            raise AuthenticationFormatCorrupted
        return public_key

    def verify(self, destructed, private_key, secret_key):
        public_key, others = destructed.verification.split('$', 1)
        timehex = others[:8]
        hexhash = others[8:]
        check_hexhash = timehash(private_key, public_key, timehex)
        if not hexhash == check_hexhash:
            raise AuthenticationHashInvalid
        given_time = int(timehex, 16)
        self.derived_context = {'time': given_time}
        if not -self.__pastlimit <= self.now() - given_time <= self.__futurelimit:
            raise AuthenticationExpired
        return True

    def merge_verification_data(self, verification, raw_data, secret_key):
        return '$'.join((verification, raw_data))

    def encode_verification(self, private_key, public_key, secret_key):
        now = self.now()
        inow = int(now)
        hextime = '%8x' % inow
        hexhash = timehash(private_key, public_key, hextime)
        return str(''.join((public_key, '$', hextime, hexhash)))

