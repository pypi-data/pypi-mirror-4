# -*- coding: utf-8 -*-
"""
Hashing and support functions

"""
from datetime import datetime
import hashlib
import hmac
from itertools import izip, starmap
from struct import Struct
from operator import xor
import os

try:
    import bcrypt
except ImportError:
    bcrypt = None
try:
    import scrypt
except ImportError:
    scrypt = None
from jinja2 import PackageLoader
from shake import url_for, Render


__all__ = (
    'split_hash', 'generate_salt', 'pbkdf2',
    'hash_sha256', 'hash_sha512', 'hash_bcrypt', 'hash_scrypt',
    'LazyUser', 'Token', 'auth_render',
)


DEFAULT_COST = 11


def split_hash(hashed):
    """Split the hashed password into it's components.
    
    Returns a tuple with the hash name, cost and salt.
        
        >>> split_hash('dsha512$13$mysalt$myhash')
        ('dsha512', 13, 'mysalt')
        >>> split_hash('bcrypt$06$mysaltyhash')
        ('bcrypt', 6, 'mysaltyhash')
    
    """
    lhashed = hashed.split('$')
    if len(lhashed) < 3:
        raise ValueError
    return lhashed[0], int(lhashed[1]), lhashed[2]


def generate_salt():
    return hashlib.sha1(os.urandom(64)).hexdigest()


_pack_int = Struct('>I').pack


def pbkdf2(data, salt, iterations=1024, keylen=24, hashfunc=None):
    """Returns an hex digest for the PBKDF2 hash algorithm of `data`
    with the given `salt`.
    It iterates `iterations` time and produces a key of `keylen` bytes.
    By default SHA-512 is used as hash function, a different hashlib `hashfunc`
    can be provided.

    Copyright (c) 2011 by Armin Ronacher. Used under the modified BSD license
    (https://github.com/mitsuhiko/python-pbkdf2/blob/master/LICENSE)
    """
    hashfunc = hashfunc or hashlib.sha512
    mac = hmac.new(key=data, msg=None, digestmod=hashfunc)

    def _pseudorandom(x, mac=mac):
        h = mac.copy()
        h.update(x)
        return map(ord, h.digest())

    buf = []
    for block in xrange(1, -(-keylen // mac.digest_size) + 1):
        rv = u = _pseudorandom(salt + _pack_int(block))
        for i in xrange(iterations - 1):
            u = _pseudorandom(''.join(map(chr, u)))
            rv = starmap(xor, izip(rv, u))
        buf.extend(rv)

    bin = ''.join(map(chr, buf))[:keylen]
    return bin.encode('hex')


def hash_sha256(data, salt=None, cost=DEFAULT_COST, keylen=24):
    """SHA256 based PBKDF2 password hashing.

    It iterates `2**iterations` time and produces a key of `keylen` bytes.
    Returns a string with the following format (without the spaces):
    "sha256 $ cost $ salt $ hashed_password"
    """
    salt = salt or generate_salt()
    iterations = 2 ** cost
    hashed = pbkdf2(data, salt, iterations, keylen, hashlib.sha256)
    return 'dsha256$%i$%s$%s' % (cost, salt, hashed)


def hash_sha512(data, salt=None, cost=DEFAULT_COST, keylen=24):
    """SHA512 based PBKDF2 password hashing.

    It iterates `2**iterations` time and produces a key of `keylen` bytes.
    Returns a string with the following format (without the spaces):
    "sha512 $ cost $ salt $ hashed_password"
    """
    salt = salt or generate_salt()
    iterations = 2 ** cost
    hashed = pbkdf2(data, salt, iterations, keylen, hashlib.sha512)
    return 'dsha512$%i$%s$%s' % (cost, salt, hashed)


def hash_bcrypt(data, hashed=None, cost=DEFAULT_COST):
    """OpenBSD Blowfish password hashing.
    
    Requires py-bcrypt <http://pypi.python.org/pypi/py-bcrypt/>
    
    It hashes passwords using a version of Bruce Schneier's Blowfish
    block cipher with modifications designed to raise the iterations of
    off-line password cracking, so it can be increased as computers get faster.
    
    Returns a string with the following format (without the spaces):
    "bcrypt $ cost $ salted_hashed_password"
    """
    assert cost >= 4
    # In this implementation of the algorithm, bcrypt hashes
    # starts with '$2a$'. This is replaced with 'bcrypt$' to maintain
    # consistency with the other hash algorithms in the module.
    if hashed:
        salt = hashed.replace('bcrypt$', '$2a$', 1)
    else:
        salt = bcrypt.gensalt(cost)
    hashed = bcrypt.hashpw(data, salt)
    return hashed.replace('$2a$', 'bcrypt$', 1)


def hash_scrypt(data, salt=None, cost=DEFAULT_COST):
    """Scrypt password hashing. (http://www.tarsnap.com/scrypt.html)
    
    Requires scrypt <http://pypi.python.org/pypi/scrypt/>
    The scrypt key derivation function (2009) is designed to be far more secure
    against hardware brute-force attacks than alternative functions such as
    PBKDF2 or bcrypt.
    
    Returns a string with the following format (without the spaces):
    "scrypt $ cost $ salt $ hashed_password"
    """
    salt = salt or generate_salt()
    iterations = 2 ** cost
    hashed = scrypt.hash(data, salt, N=iterations).encode('hex')
    return 'scrypt$%i$%s$%s' % (cost, salt, hashed)


def hash_old_sha256(data, salt=None, cost=DEFAULT_COST):
    """Old version of the SHA-256 password hashing function.
    Not for general use, Included here only to upgrade old hashes.
    """
    salt = salt or hashlib.sha256(os.urandom(64)).hexdigest()
    hashed = hashlib.sha256(salt + data).hexdigest()
    # Key strengthening
    for i in xrange(2 ** cost):
        hashed = hashlib.sha256(hashed + salt).hexdigest()
    return 'sha256$%i$%s$%s' % (cost, salt, hashed)


def hash_old_sha512(data, salt=None, cost=DEFAULT_COST):
    """Old version of the SHA-512 password hashing function.
    Not for general use. Included here only to upgrade old hashes.
    """
    salt = salt or hashlib.sha512(os.urandom(64)).hexdigest()
    hashed = hashlib.sha512(salt + data).hexdigest()
    # Key strengthening
    for i in xrange(2 ** cost):
        hashed = hashlib.sha512(hashed + salt).hexdigest()
    return 'sha512$%i$%s$%s' % (cost, salt, hashed)


def get_user_hmac(user):
    # This use as a seed a few chars from the password SALT.
    # NOT from the real password.
    mac = hashlib.sha256(user.password[10:18])
    mac = mac.hexdigest()[:8]
    return '%s$%s' % (user.id, mac)


class LazyUser(object):
    """Loads the current user from the session, but only when needed.
    
    Instead of just storing the user id, we generate a hash from the
    password *salt*. That way, an admin or the user herself can invalidate
    the login in other computers just by changing (or re-saving) her password.
    """

    SESSION_NAME = '_uhm'
    
    def __init__(self, app, db, User):
        self.db = db
        self.User = User
    
    def __get__(self, request, obj_type=None):
        user = None
        uhmac = request.session.get(self.SESSION_NAME)
        if uhmac:
            try:
                uid, mac = uhmac.split('$')
                user = self.db.query(self.User).get(uid)
                if not user or uhmac != get_user_hmac(user):
                    raise ValueError
            except ValueError:
                user = None
                self.app.session_interface.invalidate(request)
        request.user = user
        return user


class Token(object):
    
    def __init__(self, token, expire_after):
        self.token = token
        self._expire_after = expire_after
    
    @property
    def expire_after(self):
        return self._expire_after
    
    @property
    def link(self):
        return url_for('auth.check_token', external=True, token=self.token)
    
    def __repr__(self):
        return self.token


auth_loader = PackageLoader('shake_auth', 'templates')
auth_render = Render(loader=auth_loader)

