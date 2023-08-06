
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
    __futurelimit = 180
    __pastlimit = 300

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
        return hexhash == check_hexhash

    def merge_verifier_data(self, verifier, raw_data, secret_key):
        return '$'.join((verifier, raw_data))

    def encode_verifier(self, private_key, public_key, secret_key):
        now = time.time()
        inow = int(now)
        hextime = '%8x' % inow
        hexhash = timehash(private_key, public_key, hextime)
        return ''.join((public_key, '$', hextime, hexhash))
