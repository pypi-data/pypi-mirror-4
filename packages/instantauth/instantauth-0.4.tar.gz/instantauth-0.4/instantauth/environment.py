
from .cryptors import PlainCryptor
from .verifiers import BypassVerifier
from .coders import BlankCoder
from .coders.urlquery import URLQueryCoder
from .coders.json import JsonCoder

class Environment(object):
    def __init__(self, cryptor=None, verifier=None, coder=None):
        self.cryptor = cryptor
        self.verifier = verifier
        self.coder = coder

nothing_environment = Environment(PlainCryptor(), BypassVerifier(), BlankCoder())
http_environment = Environment(PlainCryptor(), BypassVerifier(), URLQueryCoder())
