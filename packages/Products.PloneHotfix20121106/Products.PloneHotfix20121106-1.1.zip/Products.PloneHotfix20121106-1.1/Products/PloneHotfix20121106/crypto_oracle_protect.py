from utils import is_equal
from plone.protect import authenticator
from zope.component import getUtility
from plone.keyring.interfaces import IKeyManager
import hmac
try:
    import sha
except:
    from hashlib import sha1 as sha


def _verify(request):
    auth = request.get("_authenticator")
    if auth is None:
        return False

    manager = getUtility(IKeyManager)
    ring = manager[u"_system"]
    user = authenticator._getUserName()

    for key in ring:
        if key is None:
            continue
        correct = hmac.new(key, user, sha).hexdigest()
        if is_equal(correct, auth):
            return True

    return False
authenticator._verify = _verify
