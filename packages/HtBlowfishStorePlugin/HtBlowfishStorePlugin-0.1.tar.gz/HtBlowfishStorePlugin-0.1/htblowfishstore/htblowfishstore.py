import bcrypt

from acct_mgr.htfile import HtPasswdStore

class HtBlowfishStore(HtPasswdStore):
    """
    This class extends HtPasswdStore for Trac's AccountManager with Blowfish support.
    """

    def config_key(self):
        return 'htblowfish'

    def userline(self, user, password):
        if self.hash_type == 'blowfish':
            return self.prefix(user) + bcrypt.hashpw(password, bcrypt.gensalt())
        else:
            return super(HtBlowfishStore, self).userline(user, password)

    def _check_userline(self, user, password, suffix):
        if suffix.startswith('$2a$'):
            return suffix == bcrypt.hashpw(password, suffix)
        else:
            return super(HtBlowfishStore, self)._check_userline(user, password, suffix)
