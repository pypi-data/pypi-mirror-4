import random
try:
    random = random.SystemRandom()
    using_sysrandom = True
except NotImplementedError:
    using_sysrandom = False

try:
    from hashlib import md5
except ImportError:
    from md5 import md5

import time

import django_crypto


try:
    from plone.keyring import keyring
    def KeyringGenerateSecret(length=64):
        return django_crypto.get_random_string(length)
    keyring.GenerateSecret = KeyringGenerateSecret
except ImportError:
    pass


try:
    from plone.openid import util
    def OpenIdGenerateSecret(length=16):
        return django_crypto.get_random_string(length)
    util.GenerateSecret = OpenIdGenerateSecret
except ImportError:
    pass


from Products.PasswordResetTool import PasswordResetTool
import socket

def uniqueString(self, userid):
    t = long(time.time() * 1000)
    r = django_crypto.get_random_string(64)
    try:
        a = socket.gethostbyname(socket.gethostname())
    except:
        # if we can't get a network address, just imagine one
        a = django_crypto.get_random_string(64)
    data = str(t) + ' ' + str(r) + ' ' + str(a)
    data = md5(data).hexdigest()
    return str(data)
PasswordResetTool.PasswordResetTool.uniqueString = uniqueString
