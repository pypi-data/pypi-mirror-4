
from hmac import new as HMAC
import hashlib
from base64 import b64decode
from time import time as epoch

def hmac_from_name(alg_name='sha256'):
    assert alg_name in hashlib.algorithms, "Hash algorithm %s not known" % alg_name
    alg_constructor = getattr(hashlib, alg_name)
    return lambda key, msg=None: HMAC(key, msg, alg_constructor)

def _hmac(msg, alg_name, key):
    hm = hmac_from_name(alg_name)
    return hm(key, msg).hexdigest()

def hmac_wrap(msg, secret):
    assert not secret['accept_only'], "Key not valid for signing"
    handle, alg_name, key = [secret[k] for k in ('name', 'type', 'key')]
    timestamp = int(epoch())
    hm_digest = _hmac(handle +'\n' + str(timestamp) + '\n' + msg, alg_name, key)
    return {'msg': msg, 'hmac': hm_digest, 'handle': handle, 'timestamp': timestamp}

def lookup_from_secrets(secrets):
    lookup = {}
    for secret in secrets:
        secret = secret.copy()
        secret['key'] = b64decode(secret['key'])
        lookup[secret['name']] = secret
    return lookup

def signers_from_secrets(secrets):
    signers = []
    for secret in secrets:
        secret = secret.copy()
        secret['key'] = b64decode(secret['key'])
        if not secret['accept_only']:
            signers.append(secret)
    return signers

def assert_hmac(msg, lookup):
    assert 'hmac' in msg, "hmac field missing"
    assert 'msg' in msg, "msg field missing"
    assert 'handle' in msg, "handle field missing"
    assert 'timestamp' in msg, "timestamp field missing"
    handle = msg['handle']
    assert handle in lookup, "Handle unknown"
    alg_name, key, max_age_secs = [lookup[handle][k] for k in ('type', 'key', 'max_age_secs')]
    assert epoch() < msg['timestamp'] + max_age_secs, "Message expired"
    hm_digest = _hmac(handle + '\n' + str(msg['timestamp']) + '\n' + msg['msg'], alg_name, key)
    assert hm_digest == msg['hmac'], "Signature invalid"
    return True

import json

class AutoHMAC(object):
    """A fully-automatic HMAC sign-and-verify service
       NOTE: This class requires a CredClient object to operate, as provided by 
       credservice."""
    def __init__(self, tellme, resource='stomp-sig'):
        """Initialize an AutoHMAC instance from a CredClient object)"""
        secrets = tellme(resource)
        self.signers = signers_from_secrets(secrets)
        self.lookup = lookup_from_secrets(secrets)

    def pack(self, obj):
        """Pack an object for transmission"""
        raw_msg = json.dumps(obj)
        return hmac_wrap(raw_msg, self.signers[0])

    def unpack(self, msg):
        """Assert and unpack a signed message"""
        assert_hmac(msg, self.lookup)
        return json.loads(msg['msg'])
