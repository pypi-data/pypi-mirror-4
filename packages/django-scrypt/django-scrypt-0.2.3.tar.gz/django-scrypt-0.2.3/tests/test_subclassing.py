# -*- coding: utf-8 -*-

from __future__ import with_statement, unicode_literals
import time
from django.conf.global_settings import PASSWORD_HASHERS as default_hashers
from django.contrib.auth.hashers import (
    is_password_usable, check_password, make_password,
    get_hasher, load_hashers, UNUSABLE_PASSWORD)
from django.utils.unittest import TestCase, skipUnless

from django_scrypt.hashers import ScryptPasswordHasher

try:
    import scrypt
except ImportError:
    scrypt = None


@skipUnless(scrypt, "Uninstalled scrypt module needed to generate hash")
class TestBigMemNScryptHasher(TestCase):

    def setUp(self):
        scrypt_hashers = (
            "tests.test_subclassing.BigMemNScryptHasher",
            "django_scrypt.hashers.ScryptPasswordHasher") + default_hashers
        load_hashers(password_hashers=scrypt_hashers)
        self.password = 'letmein'

    def test_BigMemScryptHasher(self):
        """Test operation of the extended bigmem hasher"""
        encoded = make_password(self.password, hasher='scrypt_N')
        self.assertTrue(check_password(self.password, encoded))


@skipUnless(scrypt, "Uninstalled scrypt module needed to generate hash")
class TestBigMemScryptHasher(TestCase):

    def setUp(self):
        scrypt_hashers = (
            "tests.test_subclassing.BigMemScryptHasher",
            "django_scrypt.hashers.ScryptPasswordHasher") + default_hashers
        load_hashers(password_hashers=scrypt_hashers)
        self.password = 'letmein'

    def test_BigMemScryptHasher(self):
        """Test operation of the extended bigmem hasher"""
        encoded = make_password(self.password, hasher='scrypt_r')
        self.assertTrue(check_password(self.password, encoded))


@skipUnless(scrypt, "Uninstalled scrypt module needed to generate hash")
class TestLongTimeScryptHasher(TestCase):

    def setUp(self):
        scrypt_hashers = (
            "tests.test_subclassing.LongTimeScryptHasher",
            "django_scrypt.hashers.ScryptPasswordHasher") + default_hashers
        load_hashers(password_hashers=scrypt_hashers)
        self.password = 'letmein'

    def test_LongTimeScryptHasher(self):
        """Test operation of the extended time hasher that uses 16MB"""
        encoded = make_password(self.password, hasher='scrypt_p')
        self.assertTrue(check_password(self.password, encoded))

    def test_LongTimeScryptHasher_takes_long_time(self):
        """Test operation of the extended time hasher uses more time than
        default
        """
        start = time.clock()
        encoded = make_password(self.password, hasher='scrypt')
        self.assertTrue(check_password(self.password, encoded))
        elapsed1 = (time.clock() - start)

        start = time.clock()
        encoded = make_password(self.password, hasher='scrypt_p')
        self.assertTrue(check_password(self.password, encoded))
        elapsed2 = (time.clock() - start)

        self.assertTrue(elapsed1 < elapsed2)


class LongTimeScryptHasher(ScryptPasswordHasher):
    """This hasher is tuned for longer duration"""
    algorithm = "scrypt_p"
    p = 3


class BigMemScryptHasher(ScryptPasswordHasher):
    """This hasher is tuned to use lots of memory
    (128 * 2 ** 14 * 18) ==  37748736 or ~36mb
    """
    algorithm = "scrypt_r"
    r = 18


class BigMemNScryptHasher(ScryptPasswordHasher):
    """This hasher is tuned to use lots of memory
    (128 * 2 ** 15 * 8) == 33554432 or ~32mb
    """
    algorithm = "scrypt_N"
    N = 15
