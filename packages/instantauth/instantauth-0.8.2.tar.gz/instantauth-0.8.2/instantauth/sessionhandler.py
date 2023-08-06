
class SessionHandler(object):
    def session_from_session_key(self, session_key, type=None):
        raise NotImplementedError

    def session_from_public_key(self, public_key):
        raise NotImplementedError

    def get_public_key(self, session):
        raise NotImplementedError

    def get_private_key(self, session):
        raise NotImplementedError
