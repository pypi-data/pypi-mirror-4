from utils import is_equal
from plone.session import tktauth
import time


def validateTicket(secret, ticket, ip='0.0.0.0', timeout=0, now=None,
                   encoding='utf8', mod_auth_tkt=False):
    try:
        (digest, userid, tokens, user_data, timestamp) = data = \
            tktauth.splitTicket(ticket)
    except ValueError:
        return None
    new_ticket = tktauth.createTicket(secret, userid, tokens,
        user_data, ip, timestamp, encoding, mod_auth_tkt)
    if is_equal(new_ticket[:32], digest):
        if not timeout:
            return data
        if now is None:
            now = time.time()
        if timestamp + timeout > now:
            return data
    return None
tktauth.validateTicket = validateTicket
