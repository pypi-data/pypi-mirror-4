
""" ``comp`` module.
"""

import sys


PY3 = sys.version_info[0] >= 3

if PY3:  # pragma: nocover
    bytes_type = bytes
    str_type = str
    chr = lambda i: bytes((i,))
    ord = lambda b: b

    def n(s, encoding='latin1'):
        if isinstance(s, str_type):
            return s
        return s.decode(encoding)

    def btos(b, encoding):
        return b.decode(encoding)

    u = lambda s: s

else:  # pragma: nocover
    bytes_type = str
    str_type = unicode
    chr = chr
    ord = ord

    def n(s, encoding='latin1'):
        if isinstance(s, bytes_type):
            return s
        return s.encode(encoding)

    def btos(b, encoding):
        return b.decode(encoding)

    u = lambda s: unicode(s, 'unicode_escape')


def b(s, encoding='latin1'):  # pragma: nocover
    if isinstance(s, bytes_type):
        return s
    return s.encode(encoding)


# Hash functions
try:  # pragma: nocover
    # Python 2.5+
    from hashlib import md5, sha1, sha224, sha256, sha384, sha512
    digest_size = lambda d: d().digest_size

    try:
        from hashlib import new as openssl_hash
        ripemd160 = lambda: openssl_hash('ripemd160')
        whirlpool = lambda: openssl_hash('whirlpool')
    except ValueError:
        ripemd160 = None
        whirlpool = None
except ImportError:  # pragma: nocover
    import md5
    import sha as sha1
    sha224 = sha256 = sha384 = sha512 = ripemd160 = whirlpool = None
    digest_size = lambda d: d.digest_size

# Encryption interface
block_size = None
encrypt = None
decrypt = None

# Supported cyphers
aes128 = None
aes192 = None
aes256 = None

# Python Cryptography Toolkit (pycrypto)
try:  # pragma: nocover
    from Crypto.Cipher import AES

    # pycrypto interface
    block_size = lambda c: c.block_size
    encrypt = lambda c, v: c.encrypt(v)
    decrypt = lambda c, v: c.decrypt(v)

    # suppored cyphers
    def aes(key, key_size=32):
        key = key[-key_size:]
        iv = key[-16:]
        return lambda: AES.new(key, AES.MODE_CBC, iv)

    aes128 = lambda key: aes(key, 16)
    aes192 = lambda key: aes(key, 24)
    aes256 = lambda key: aes(key, 32)
except ImportError:  # pragma: nocover
    # TODO: add fallback to other encryption providers
    pass
