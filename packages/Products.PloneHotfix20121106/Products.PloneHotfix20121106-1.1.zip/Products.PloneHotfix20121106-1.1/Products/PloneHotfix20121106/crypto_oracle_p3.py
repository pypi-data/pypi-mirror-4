import plone.session.sources.hash
from utils import is_equal


def verifyIdentifier(self, identifier):
    for secret in self.getSecrets():
        try:
            (signature, userid)=self.splitIdentifier(identifier)
            if is_equal(signature, self.signUserid(userid, secret)):
                return True
        except (AttributeError, ValueError):
            continue

    return False
plone.session.sources.hash.verifyIdentifier = verifyIdentifier
