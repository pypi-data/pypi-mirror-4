# -*- coding: utf-8 -*-
"""Create and store Scrypt message digests
"""
from __future__ import unicode_literals
import sys
import base64
from django.contrib.auth.hashers import BasePasswordHasher, mask_hash
from django.utils.datastructures import SortedDict
from django.utils.crypto import constant_time_compare
from django.utils.translation import ugettext_noop as _

import scrypt


PYTHON3 = sys.version_info >= (3, 0)


def enbase64(s):
    """Returns Base64 encoded bytes without linefeeds"""
    return base64.b64encode(s)


def debase64(s):
    """Decodes Base64 encoded bytes with or without linefeeds"""
    if PYTHON3 and isinstance(s, str):
        s = bytes(s, 'utf-8')
    return base64.b64decode(s)


def stringify(s):
    """Returns a stripped string appropriate for a Scrypt hash function

    Returns UTF-8 encoded string if Python 2 or
            Unicode string if Python 3
    """
    if PYTHON3:
        if type(s) is bytes:
            return s.decode('utf-8').strip()
        else:
            return s.strip()
    else:
        if type(s) is unicode:
            return s.encode('utf-8').strip()
        else:
            return str(s).strip()


def remove_linefeeds_from_base64_hash(hash):
    """Cleans the Base64 fragment of linefeeds"""
    algorithm, salt, Nexp, r, p, buflen, h = hash.split('$')
    h = enbase64(debase64(h))
    hash = "$".join([algorithm, salt, Nexp, r, p, buflen, stringify(h)])
    return hash


class ScryptPasswordHasher(BasePasswordHasher):
    """
    A secure password hasher using the Scrypt algorithm

    This subclass overrides the 'verify', 'encode', and 'safe_summary'
    methods of BasePasswordHasher to allow Django to use the Scrypt
    memory-hard key derivation function.

    Subclass to modify parameters for custom Scrypt tuning.

    The Py-Scrypt library must be installed separately. That library
    depends on native C code and may cause portability issues.

    Class Attributes

    algorithm -- Unique algorithm identifier used in encoded digests
    library -- Import name of the required Py-Scrypt library
    Nexp -- Default exponent value used to calculate N = 2 ** Nexp
    r -- Default r-value used by Scrypt as positive integer
    p -- Default p-value used by Scrypt as positive integer
    buflen -- Unimplemented, holds byte length of the message digest

    """

    algorithm = "scrypt"
    library = ("scrypt")
    Nexp = 14  # N == 2 ** 14 == 16384
    r = 8
    p = 1
    buflen = 64

    def verify(self, password, encoded):
        """
        Checks if the given password is correct

        password -- Password to be verified
        encoded -- An encoded Scrypt message digest for comparison

        Returns boolean True or False

        """
        assert encoded
        encoded = remove_linefeeds_from_base64_hash(encoded)
        algorithm, salt, Nexp, r, p, buflen, h = encoded.split('$')
        assert algorithm == self.algorithm
        # TODO: buflen is an experimental proposal in py-scrypt
        hashp = self.encode(password, salt, int(Nexp), int(r), int(p))
        return constant_time_compare(encoded, hashp)

    def encode(self, password, salt, Nexp=None, r=None, p=None, buflen=None):
        """
        Creates an encoded hash string from password, salt and optional
        parameters.

        When used with a custom subclass, this method may return strings
        longer than 128 characters (Django 1.4 password length limit)

        password -- User's chosen password
        salt -- Random string, 12-characters [a-zA-Z0-9] by default
        Nexp -- Exponent for N such that N = 2 ** Nexp, Nexp = 14 means
            N = 2 ** 14 = 16384 which is the value passed to the
            Scrypt module. Must be a positive integer >= 1.
        r -- The r-value passed to Scrypt as a positive integer
        p -- The p-value passed to Scrypt as a positive integer
        buflen -- Length of the returned hash in bytes (not implemented)

        Returns "scrypt$salt$Nexp$r$p$buflen$hash" where hash is a base64
        encoded byte string (64-bytes or 512-bits by default)

        """
        assert password
        password = stringify(password)
        assert salt
        salt = stringify(salt)
        assert '$' not in salt
        hashed = [self.algorithm]
        hashed.append(salt)
        if not Nexp:
            Nexp = self.Nexp
        if not r:
            r = self.r
        if not p:
            p = self.p
        if not buflen:
            buflen = self.buflen
        # TODO: buflen is an experimental proposal in py-scrypt
        buflen = self.buflen
        hashed.append(str(Nexp))
        hashed.append(str(r))
        hashed.append(str(p))
        hashed.append(str(buflen))
        h = scrypt.hash(password, salt, 2 ** Nexp, r, p)
        hashed.append(stringify(enbase64(h)))
        return "$".join(hashed)

    def safe_summary(self, encoded):
        """
        Returns a summary of safe values

        encoded -- An encoded hash (see encode method for format)

        Returns a dictionary (SortedDict) used when password info
        must be displayed

        """
        algorithm, salt, Nexp, r, p, buflen, h = encoded.split('$')
        assert algorithm == self.algorithm
        return SortedDict([
            (_('algorithm'), algorithm),
            (_('salt'), mask_hash(salt, show=2)),
            (_('Nexp'), Nexp),
            (_('r'), r),
            (_('p'), p),
            (_('buflen'), buflen),
            (_('hash'), mask_hash(h)),
        ])
