
import time
import hashlib
from . import Verifier

def timehash(private_key, public_key, hextime):
    m = hashlib.sha1()
    m.update(private_key)
    m.update(public_key)
    m.update(hextime)
    return m.hexdigest()

class TimeHashVerifier(Verifier):
    def __init__(self, limits=(300, 180)):
        self.__pastlimit, self.__futurelimit = limits

    def divide_verifier_data(self, raw_data, secret_key):
        return raw_data.rsplit('$', 1)

    def public_key_from_verifier(self, verifier, secret_key):
        public_key, others = verifier.split('$', 1)
        return public_key
    
    def verify(self, verifier, private_key, secret_key):
        public_key, others = verifier.split('$', 1)
        timehex = others[:8]
        hexhash = others[8:]
        check_hexhash = timehash(private_key, public_key, timehex)
        if not hexhash == check_hexhash:
            return False
        given_time = int(timehex, 16)
        self.derived_context = {'time': given_time}
        return -self.__pastlimit <= time.time() - given_time <= self.__futurelimit

    def merge_verifier_data(self, verifier, raw_data, secret_key):
        return '$'.join((verifier, raw_data))

    def encode_verifier(self, private_key, public_key, secret_key):
        now = time.time()
        inow = int(now)
        hextime = '%8x' % inow
        hexhash = timehash(private_key, public_key, hextime)
        return ''.join((public_key, '$', hextime, hexhash))

