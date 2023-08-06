# -*- coding: utf-8 -*-

from __future__ import with_statement, unicode_literals
import sys
import django
from django.conf.global_settings import PASSWORD_HASHERS as default_hashers
from django.contrib.auth.hashers import (
    is_password_usable, check_password, make_password,
    get_hasher, load_hashers, UNUSABLE_PASSWORD)
from django.utils.unittest import TestCase, skipUnless
from django.utils.translation import ugettext_noop as _

import django_scrypt
from django_scrypt.hashers import (
    ScryptPasswordHasher, enbase64, debase64, stringify,
    remove_linefeeds_from_base64_hash)

try:
    import scrypt
except ImportError:
    scrypt = None


PYTHON3 = sys.version_info >= (3, 0)
DJANGO15 = (django.VERSION > (1, 5, 0) and django.VERSION < (1, 6, 0))


def utf8(b):
    """Returns Unicode string given UTF-8 encoded string"""
    return b.decode('utf-8')


@skipUnless(utf8, "UTF-8 helper is required")
class TestUTF8Helper(TestCase):
    def setUp(self):
        self.utf8_encoded = b'a\xc2\xac\xe1\x88\xb4\xe2\x82\xac\xe8\x80\x80'

    @skipUnless(not PYTHON3, "Python 2.X required")
    def test_unicode_from_python_2(self):
        """Given UTF-8 encoded bytes obtain Unicode string"""
        unicode_str = utf8(self.utf8_encoded)
        self.assertTrue(isinstance(self.utf8_encoded, str))
        self.assertTrue(isinstance(unicode_str, unicode))

    @skipUnless(PYTHON3, "Python 3.X required")
    def test_unicode_from_python_3(self):
        """Given UTF-8 encoded bytes obtain Unicode string"""
        unicode_str = utf8(self.utf8_encoded)
        self.assertTrue(isinstance(self.utf8_encoded, bytes))
        self.assertTrue(isinstance(unicode_str, str))


class TestHelpers(TestCase):
    def setUp(self):
        self.utf8_encoded = b'a\xc2\xac\xe1\x88\xb4\xe2\x82\xac\xe8\x80\x80'
        self.unicode_str = utf8(self.utf8_encoded)
        self.test_str = b'Test'
        self.test_str_base64 = b'VGVzdA=='
        self.test_str_base64_lf = b'VGVzdA==\n'

    def test_enbase64(self):
        """Returns a Base64 encoded string"""
        encoded = enbase64(self.test_str)
        expected = self.test_str_base64
        self.assertEqual(encoded, expected)
        self.assertTrue(isinstance(encoded, bytes))

    def test_debase64(self):
        """Decodes a Base64 encoded string"""
        decoded = debase64(self.test_str_base64)
        expected = self.test_str
        self.assertEqual(decoded, expected)
        self.assertTrue(isinstance(decoded, bytes))
        decoded = debase64(self.test_str_base64_lf)
        expected = self.test_str
        self.assertEqual(decoded, expected)
        self.assertTrue(isinstance(decoded, bytes))

    @skipUnless(not PYTHON3, "Python 2 required")
    def test_stringify_py2(self):
        """String returned is suitable for use by hasher"""
        # String is already UTF-8 encoded, it should pass
        self.assertTrue(isinstance(stringify(self.utf8_encoded), str))
        # Unicode string is encoded to UTF-8
        self.assertTrue(isinstance(stringify(self.unicode_str), str))

    @skipUnless(PYTHON3, "Python 3 required")
    def test_stringify_py3(self):
        """String returned is suitable for use by hasher"""
        # Input bytes are UTF-8 encoded, it should pass
        self.assertTrue(isinstance(stringify(self.utf8_encoded), str))
        # Unicode string is encoded to UTF-8
        self.assertTrue(isinstance(stringify(self.unicode_str), str))

    def test_remove_linefeeds_from_base64_hash(self):
        """Hashes are cleaned of linefeeds"""
        hash_lf = (
            'scrypt$h64FF0EdQ1f9$14$8$1$64$refoMN0aZci6vt0VOPKB7tfgPS/wgAWXxz'
            'e1z8CSzTzVSUV0hT3ByyE3YKPCpOegxJfZ6CZgQ+DS\nhd3G65p24Q==')
        hash = (
            'scrypt$h64FF0EdQ1f9$14$8$1$64$refoMN0aZci6vt0VOPKB7tfgPS/wgAWXxz'
            'e1z8CSzTzVSUV0hT3ByyE3YKPCpOegxJfZ6CZgQ+DShd3G65p24Q==')
        unicode_pwd = 'a\xac\u1234\u20ac\u8000'
        h = remove_linefeeds_from_base64_hash(hash_lf)
        self.assertTrue(check_password(unicode_pwd, h))
        h = remove_linefeeds_from_base64_hash(hash)
        self.assertTrue(check_password(unicode_pwd, h))


@skipUnless(scrypt, "Uninstalled scrypt module needed to generate hash")
class TestDjangoScrypt(TestCase):

    def setUp(self):
        scrypt_hashers = (
            "django_scrypt.hashers.ScryptPasswordHasher",) + default_hashers
        load_hashers(password_hashers=scrypt_hashers)
        self.password = 'letmein'
        self.unicode_text = utf8(
            b'\xe1\x93\x84\xe1\x93\x87\xe1\x95\x97\xe1\x92\xbb\xe1\x92\xa5\xe1'
            b'\x90\x85\xe1\x91\xa6')
        self.bad_password = 'letmeinz'
        self.expected_hash_prefix = "scrypt"
        self.old_format_encoded_hash = (
            "scrypt$FYY1dftUuK0b$16384$8$1$64$/JYOBEED7nMzJgvlqfzDj1JKGVLup0e"
            "YLyG39WA2KCywgnB1ubN0uzFYyaEQthINm6ynjjqr+D+U\nw5chi74WVw==")
        self.old_format_fix_encoded_hash = (
            "scrypt$FYY1dftUuK0b$14$8$1$64$/JYOBEED7nMzJgvlqfzDj1JKGVLup0eYLy"
            "G39WA2KCywgnB1ubN0uzFYyaEQthINm6ynjjqr+D+U\nw5chi74WVw==")
        self.encoded_hash = (
            "scrypt$gwQg9TZ3eyub$14$8$1$64$lQhi3+c0xkYDUj35BvS6jVTlHRAH/RS4nk"
            "pd1tKMc0r9PcFyjCjPj1k9/CkSCRvcTvHiWfFYpHfB\nZDCHMNIeHA==")

    def test_version_string_set(self):
        """Test for version string on package"""
        self.assertTrue(type(django_scrypt.__version__), str)
        self.assertTrue(len(django_scrypt.__version__) > 0)

    def test_encoder_default_hash_less_than_128_characters(self):
        """Test that returned encoded hash is less than db limit of 128
        characters
        """
        encoded = make_password(self.password)
        self.assertTrue(len(encoded) < 128)

    def test_encoder_accepts_unicode(self):
        """Test that passwords can be Unicode"""
        encoded = make_password(self.unicode_text)
        self.assertTrue(check_password(self.unicode_text, encoded))

    def test_encoder_specified_scrypt_hasher(self):
        """Test hasher is obtained by name"""
        encoded = make_password(self.password, hasher='scrypt')
        self.assertTrue(check_password(self.password, encoded))

    def test_encoder_hash_usable(self):
        """Test encoder returns usable hash string"""
        encoded = make_password(self.password)
        self.assertTrue(is_password_usable(encoded))

    def test_encoder_hash_starts_with_algorithm_string(self):
        """Test that encoded hash string has correct prefix with first
        separator
        """
        encoded = make_password(self.password)
        self.assertTrue(encoded.startswith(self.expected_hash_prefix + "$"))

    def test_encoder_hash_has_required_sections(self):
        """Test encoder returns hash with required sections"""
        encoded = make_password(self.password)
        algorithm, salt, Nexp, r, p, buflen, h = encoded.split('$')
        self.assertEqual(algorithm, self.expected_hash_prefix)
        self.assertTrue(len(salt))
        self.assertTrue(Nexp.isdigit())
        self.assertTrue(r.isdigit())
        self.assertTrue(p.isdigit())
        self.assertTrue(buflen.isdigit())
        self.assertTrue(len(h))

    def test_safe_summary_has_required_sections(self):
        """Test safe_summary returns string with required informative
        sections
        """
        encoded = make_password(self.password)
        hasher = get_hasher('scrypt')
        d = hasher.safe_summary(encoded)
        self.assertEqual(d[_('algorithm')], self.expected_hash_prefix)
        self.assertTrue(len(d[_('salt')]))
        self.assertTrue(d[_('Nexp')].isdigit())
        self.assertTrue(d[_('r')].isdigit())
        self.assertTrue(d[_('p')].isdigit())
        self.assertTrue(d[_('buflen')].isdigit())
        self.assertTrue(len(d[_('hash')]))

    def test_verify_bad_passwords_fail(self):
        """Test verify method causes failure on mismatched passwords"""
        encoded = make_password(self.password)
        self.assertFalse(check_password(self.bad_password, encoded))

    def test_verify_passwords_match(self):
        """Test verify method functions via check_password"""
        encoded = make_password(self.password)
        self.assertTrue(check_password(self.password, encoded))

    def test_verify_default_hash_format_usable(self):
        """Test encoded format passes good password"""
        self.assertTrue(check_password(self.password, self.encoded_hash))

    def test_verify_old_hash_format_raises_error(self):
        """Ensure deprecated, old encoded hash format raises an Exception

        The old-format hashes store N == 16384 whereas new format stores
        Nexp == 14.

        The fix is to replace 16384 with 14 in each hash.
        """
        with self.assertRaises(Exception) as cm:
            check_password(self.password, self.old_format_encoded_hash)
        self.assertTrue(
            str(cm.exception) in (
                'could not compute hash',
                'hash parameters are wrong (r*p should be < 2**30, and N '
                'should be a power of two > 1)'
            )
        )

    def test_verify_old_hash_format_fixable(self):
        """Test deprecated encoded format can be fixed by swapping Nexp for N

        Specifically, replace 16384 with 14 at position 3 of the encoded hash
        """
        self.assertTrue(check_password(self.password,
                                       self.old_format_fix_encoded_hash))

    def test_class_algorithm_string_matches_expected(self):
        """Test django_scrypt algorithm string matches expected value
        'scrypt'
        """
        self.assertEqual(ScryptPasswordHasher.algorithm,
                         self.expected_hash_prefix)

    def test_no_upgrade_on_incorrect_pass(self):
        self.assertEqual('scrypt', get_hasher('default').algorithm)
        for algo in ('sha1', 'md5'):
            encoded = make_password(self.password, hasher=algo)
            state = {'upgraded': False}

            def setter():
                state['upgraded'] = True
            self.assertFalse(check_password(self.bad_password,
                                            encoded, setter))
            self.assertFalse(state['upgraded'])

    def test_no_upgrade(self):
        encoded = make_password(self.password)
        state = {'upgraded': False}

        def setter():
            state['upgraded'] = True
        self.assertFalse(check_password(self.bad_password, encoded, setter))
        self.assertFalse(state['upgraded'])

    def test_upgrade(self):
        self.assertEqual('scrypt', get_hasher('default').algorithm)
        for algo in ('sha1', 'md5'):
            encoded = make_password(self.password, hasher=algo)
            state = {'upgraded': False}

            def setter(password):
                state['upgraded'] = True

            self.assertTrue(check_password(self.password, encoded, setter))
            self.assertTrue(state['upgraded'])

    @skipUnless(DJANGO15, "Test requires Django 1.5")
    def test_upgrade_14_to_15(self):
        """Hash encoded with Django 1.4 works with Django 1.5"""
        django_14_hash = (
            'scrypt$YfVpr72fFnUk$14$8$1$64$TULcyO5CycVvRBM7q6Bw4XNozJe0NwlOQu'
            'llq102Hn6r9OsgmHTAqzDBC4e8kklF9mcChavVtqKz\n0N6s+2q7tQ==')
        self.assertTrue(check_password(self.unicode_text, django_14_hash))

    @skipUnless(PYTHON3, "Requires Python 3")
    def test_cross_interpreter_portability(self):
        """Hash encoded with Python 2 usable on system with Python 3"""
        py26_hash = (
            'scrypt$h64FF0EdQ1f9$14$8$1$64$refoMN0aZci6vt0VOPKB7tfgPS/wgAWXxz'
            'e1z8CSzTzVSUV0hT3ByyE3YKPCpOegxJfZ6CZgQ+DS\nhd3G65p24Q==')
        unicode_pwd = 'a\xac\u1234\u20ac\u8000'
        self.assertTrue(check_password(unicode_pwd, py26_hash))

    def test_base64_linefeed_indifferent(self):
        """Hashes with linefeeds work the same as hashes without"""
        py26_hash_lf = (
            'scrypt$h64FF0EdQ1f9$14$8$1$64$refoMN0aZci6vt0VOPKB7tfgPS/wgAWXxz'
            'e1z8CSzTzVSUV0hT3ByyE3YKPCpOegxJfZ6CZgQ+DS\nhd3G65p24Q==')
        py26_hash = (
            'scrypt$h64FF0EdQ1f9$14$8$1$64$refoMN0aZci6vt0VOPKB7tfgPS/wgAWXxz'
            'e1z8CSzTzVSUV0hT3ByyE3YKPCpOegxJfZ6CZgQ+DShd3G65p24Q==')
        unicode_pwd = 'a\xac\u1234\u20ac\u8000'
        self.assertTrue(check_password(unicode_pwd, py26_hash))
        self.assertTrue(check_password(unicode_pwd, py26_hash_lf))
