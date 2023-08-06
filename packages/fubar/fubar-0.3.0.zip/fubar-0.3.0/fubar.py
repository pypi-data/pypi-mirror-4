""" fubar: PBKDF2-AES-CTR-HMAC-SHA256-RSA-PKCS#1-OAEP-PSS-bencode wrapper """
import base64
import time
import zlib
import textwrap

import bencode
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.Hash import HMAC, SHA256
from Crypto.Protocol.KDF import PBKDF2
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes
from Crypto.Signature import PKCS1_PSS
from Crypto.Util import Counter


KEY_SIZE = 256 // 8
BLOCK_SIZE = AES.block_size
HALF_BLOCK_SIZE = BLOCK_SIZE // 2
HALF_BLOCK_BITS = HALF_BLOCK_SIZE * 8
KDF_FACTOR = 12
NONCE_SIZE = 128 // 8

def _aes_ctr(nonce, key):
    counter = Counter.new(HALF_BLOCK_BITS, prefix=nonce[:HALF_BLOCK_SIZE])
    return AES.new(key, mode=AES.MODE_CTR, counter=counter)

def _hmac_sha256(key, data):
    return HMAC.new(key, data, SHA256).digest()

def _derive_key(password, nonce, kdfcount, size=KEY_SIZE):
    return PBKDF2(password, nonce, dkLen=size, count=kdfcount, prf=_hmac_sha256)

def _derive_keys(password, nonce, kdfcount, size=KEY_SIZE):
    dk = _derive_key(password, nonce, kdfcount, 2 * size)
    return dk[:size], dk[size:]

def encrypt(password, data, factor=KDF_FACTOR):
    """ Encrypt data with a password """
    nonce = get_random_bytes(NONCE_SIZE)
    cryptkey, hmackey = _derive_keys(password, nonce, kdfcount=2**factor)
    cipher = _aes_ctr(nonce, cryptkey).encrypt(data)
    hmac = _hmac_sha256(hmackey, cipher)
    return bencode.bencode([factor, nonce, cipher, hmac])

def decrypt(password, data):
    """ Decrypt data and return original data if everything is ok, otherwise
    raise ValueError """
    [factor, nonce, cipher, hmac] = bencode.bdecode(data)
    cryptkey, hmackey = _derive_keys(password, nonce, kdfcount=2**factor)
    hmac2 = _hmac_sha256(hmackey, cipher)
    # anti-timing-attack by double-hmac
    if _hmac_sha256(hmackey, hmac2) != _hmac_sha256(hmackey, hmac):
        raise ValueError("Bad HMAC")
    return _aes_ctr(nonce, cryptkey).decrypt(cipher)

def _pkcs1_pss(key):
    return PKCS1_PSS.new(RSA.importKey(key))

def sign(key, data):
    """ Add signature to data """
    sig = _pkcs1_pss(key).sign(SHA256.new(data))
    return bencode.bencode([data, sig])

def unsign(key, data):
    """ Verify signed data, if verified, return original data, otherwise
    raise ValueError """
    [d, sig] = bencode.bdecode(data)
    if not _pkcs1_pss(key).verify(SHA256.new(d), sig):
        raise ValueError("Bad signature")
    return d

def _pkcs1_oaep(key):
    return PKCS1_OAEP.new(RSA.importKey(key))

def seal(key, data):
    """ Seal data with recipient's public key, only one who has the private
    key can unseal it """
    cryptkey = get_random_bytes(KEY_SIZE)
    cipher = encrypt(cryptkey, data)
    sealedkey = _pkcs1_oaep(key).encrypt(cryptkey)
    return bencode.bencode([sealedkey, cipher])

def unseal(key, data):
    """ Unseal data with a private key """
    [sealedkey, cipher] = bencode.bdecode(data)
    cryptkey = _pkcs1_oaep(key).decrypt(sealedkey)
    return decrypt(cryptkey, cipher)

def stamp(data, maxage=-1, timestamp=None):
    """ Add timestamp to data, if maxage >= 0, data will be expired at
    timestamp + maxage """
    if timestamp is None:
        timestamp = time.time()
    return bencode.bencode([data, int(timestamp), maxage])

def unstamp(data, now=None):
    """ Return timestamp removed data, or raise ValueError if it has
    expired """
    [d, timestamp, maxage] = bencode.bdecode(data)
    if now is None:
        now = time.time()
    if maxage >= 0 and now >= timestamp + maxage:
        raise ValueError("Data Expired")
    return d

def wrap(data, key, signkey=None, sealkey=None, maxage=-1, timestamp=None):
    """ Wrap data """
    compressed = zlib.compress(data)
    stamped = stamp(compressed, maxage=maxage, timestamp=timestamp)
    signed = sign(signkey, stamped) if signkey else stamped
    encrypted = encrypt(key, signed)
    sealed = seal(sealkey, encrypted) if sealkey else encrypted
    encoded = textwrap.fill(base64.b64encode(sealed), width=76)
    return encoded

def unwrap(data, key, signkey=None, sealkey=None, now=None):
    """ Unwrap data """
    decoded = base64.b64decode(data)
    unsealed = unseal(sealkey, decoded) if sealkey else decoded
    decrypted = decrypt(key, unsealed)
    unsigned = unsign(signkey, decrypted) if signkey else decrypted
    unstamped = unstamp(unsigned, now=now)
    decompressed = zlib.decompress(unstamped)
    return decompressed
