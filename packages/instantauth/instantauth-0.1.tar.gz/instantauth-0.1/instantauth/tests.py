
import time
from instantauth import Authentication, Environment, SessionHandler
from instantauth.cryptors import PlainCryptor
from instantauth.cryptors.aes import AESCryptor
from instantauth.verifiers import BypassVerifier
from instantauth.verifiers.timehash import TimeHashVerifier
from instantauth.coders.urlquery import URLQueryCoder, SimpleURLQueryCoder
from instantauth.coders.json import JsonCoder

session = {'id':0}

class TestSessionHandler(SessionHandler):
    def session_from_public_key(self, public_key):
        return session

    def get_public_key(self, session):
        return 'public_key'

    def get_private_key(self, session):
        return 'private_key'

env = Environment(PlainCryptor(), BypassVerifier(), URLQueryCoder())
auth = Authentication(env, TestSessionHandler(), 'SECRET')

data = ''
context = auth.get_context(data)
assert context.data == {}

data = 'field=value'
context = auth.get_context(data)
assert context.data == {'field': ['value']}

data = 'field=value&field=value'
context = auth.get_context(data)
assert context.data == {'field': ['value', 'value']}

env = Environment(PlainCryptor(), BypassVerifier(), SimpleURLQueryCoder())
auth = Authentication(env, TestSessionHandler(), 'SECRET')

data = 'field=value'
context = auth.get_context(data)
assert context.data == {'field': 'value'}

env = Environment(PlainCryptor(), BypassVerifier(), JsonCoder())
auth = Authentication(env, TestSessionHandler(), 'SECRET')

data = '{"field": "value"}'
context = auth.get_context(data)
assert context.data == {'field': 'value'}

private_key = ('private_key' + '!' * 40)[:40]
public_key = ('public_key' + '!' * 40)[:40]
class KeyCheckSessionHandler(SessionHandler):
    def session_from_public_key(a_public_key, secret_key):
        assert a_public_key == public_key 
        return session

    def get_private_key(session, secret_key):
        return private_key

verifier = TimeHashVerifier()
env = Environment(PlainCryptor(), verifier, SimpleURLQueryCoder())
auth = Authentication(env, TestSessionHandler(), 'SECRET')

data = {'field': 'value'}
encrypted = auth.build_data(session, data)
assert encrypted.startswith('public_key')
assert '$' in encrypted

context = auth.get_context(encrypted)
assert context.data == data


env = Environment(AESCryptor(128), verifier, SimpleURLQueryCoder())
auth = Authentication(env, TestSessionHandler(), 'SECRET')
encrypted = auth.build_data(session, data)

context = auth.get_context(encrypted)
assert context.data == data
