
from prettyexc import PrettyException

class AuthenticationError(PrettyException):
    pass

class Authentication(object):
    def __init__(self, cryptor, verifier, coder, session_handler, secret_key):
        self.cryptor = cryptor
        self.verifier = verifier
        self.coder = coder
        self.session_handler = session_handler
        self.secret_key = secret_key

    def _merge_context(self, context):
        for k, v in self.cryptor.derived_context.items():
            setattr(context, k, v)
        for k, v in self.verifier.derived_context.items():
            setattr(context, k, v)
        for k, v in self.coder.derived_context.items():
            setattr(context, k, v)

    def get_first_context(self, data, type=None):
        """
        Decode process:

        | #1 Sender-Encrypted Raw Data |
                       |
                    cryptor
                       V
        | #2 Receiver-Decrypted Raw Data | --verifier--> | Public Key |
                      |                                        |
                   verifier                                    V
                      V                                        |
          | #3 Sender-Encrypted Data | ---------->-------------+
                                                               |
                                                            cryptor
                                                               V
          | #5 Receiver-Decoded Data | <--coder-- | #4 Sender-Encoded Data |

        """
        #1: data
        decrypted = self.cryptor.decrypt_global(data, self.secret_key) #2
        destructed = self.verifier.destruct_first_data(decrypted, self.secret_key) #3
        raw_data = self.cryptor.decrypt_first_data(destructed.data, self.secret_key) #4
        semantic_data = self.coder.decode(raw_data) #5
        context = Context(None, semantic_data)
        context.session = self.session_handler.session_from_session_key(destructed.public_key, type)
        self._merge_context(context)
        return context

    def get_context(self, data):
        """
        Decode process:

        | #1 Sender-Encrypted Raw Data |
                       |
                    cryptor
                       V
        | #2 Receiver-Decrypted Raw Data | --verifier--> | Public Key | --session_handler--> | Session |
                      |                                        |                                  |
                   verifier                                    V                            session_handler
                      V                                        |                                  V
          | #3 Sender-Encrypted Data | ---------->-------------+--------------<------------ | Private Key |
                                                               |
                                                            cryptor
                                                               V
          | #5 Receiver-Decoded Data | <--coder-- | #4 Sender-Encoded Data |

        """
        #1: data
        decrypted = self.cryptor.decrypt_global(data, self.secret_key) #2
        destructed = self.verifier.destruct_data(decrypted, self.secret_key) #3
        if not destructed.public_key:
            raise AuthenticationError
        try:
            session = self.session_handler.session_from_public_key(destructed.public_key)
        except KeyError:
            raise AuthenticationError('no public key found')
        if not session:
            raise AuthenticationError('no session found')

        private_key = self.session_handler.get_private_key(session)
        raw_data = self.cryptor.decrypt_data(destructed.data, private_key, self.secret_key) #4
        semantic_data = self.coder.decode(raw_data) #5
        if not self.verifier.verify(destructed, private_key, self.secret_key):
            raise AuthenticationError
        context = Context(session, semantic_data)
        self._merge_context(context)
        return context

    def build_first_data(self, data, session_key):
        """
        Encode process:

        """
        #1 data
        coded_data = self.coder.encode(data) #2
        encrypted_data = self.cryptor.encrypt_first_data(coded_data, self.secret_key) #3
        merged_data = self.verifier.construct_first_data(encrypted_data, session_key, self.secret_key) #4
        encrypted = self.cryptor.encrypt_global(merged_data, self.secret_key) #5
        return encrypted

    def build_data(self, data, session):
        """
        Encode process:

        | #1 Original Data | --coder--> | #2 Encoded Data | --cryptor--> | #3 Encrypted Data |
                                                                                   |
                                                                                verifier
                                                                                   V
                           | #5 Encrypted Packed Data | <--cryptor-- | #4 Verification-Packed Data |

        """
        #1: data
        private_key = self.session_handler.get_private_key(session)
        public_key = self.session_handler.get_public_key(session)
        coded_data = self.coder.encode(data) #2
        assert(coded_data is not None)
        encrypted_data = self.cryptor.encrypt_data(coded_data, private_key, self.secret_key) #3
        assert(encrypted_data is not None)
        merged_data = self.verifier.construct_data(encrypted_data, private_key, public_key, self.secret_key) #4
        encrypted = self.cryptor.encrypt_global(merged_data, self.secret_key) #5
        return encrypted


class Context(object):
    def __init__(self, session, data):
        self.session = session
        self.data = data
