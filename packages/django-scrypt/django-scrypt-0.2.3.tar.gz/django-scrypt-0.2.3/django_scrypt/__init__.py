# -*- coding: utf-8 -*-
"""A Scrypt-enabled password hasher for Django 1.4/1.5

Django-Scrypt provides a Scrypt-enabled hashing class compatible
with Django's flexible password storage system

Modules

hashers - Class used for creating Scrypt message digests

Classes

hashers.ScryptPasswordHasher - Scrypt hashing for Django 1.4/1.5

Typical Usage

Place the full name of the ScryptPasswordHasher at the very top
of the PASSWORD_HASHERS tuple in your project settings file. As
users login they will update their passwords to use Scrypt hashes.

In settings.py:

PASSWORD_HASHERS = (
'django_scrypt.hashers.ScryptPasswordHasher',
'django.contrib.auth.hashers.PBKDF2PasswordHasher',
'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
'django.contrib.auth.hashers.SHA1PasswordHasher',
'django.contrib.auth.hashers.MD5PasswordHasher',
'django.contrib.auth.hashers.CryptPasswordHasher',
)
"""


from __future__ import unicode_literals


__version__ = '0.2.3'
__all__ = ['hashers']
