#!/usr/bin/env python

import os
import sys
from distutils.core import setup, Command

from django_scrypt import __version__

cmdclasses = dict()
README_PATH = os.path.join(os.path.abspath(os.path.dirname(__file__)),
                           'README.rst')
long_description = open(README_PATH, 'r').read()


class Tester(Command):
    """Runs django-scrypt unit tests"""

    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        try:
            from django.utils.unittest import TextTestRunner, defaultTestLoader
            from django.conf import settings
            settings.configure(
                USE_I18N=True
            )
        except ImportError:
            print("Please install Django => 1.4 to run the test suite")
            exit(-1)
        from tests import test_django_scrypt, test_subclassing
        suite = defaultTestLoader.loadTestsFromModule(test_django_scrypt)
        suite.addTests(defaultTestLoader.loadTestsFromModule(test_subclassing))
        runner = TextTestRunner()
        result = runner.run(suite)
        if result.wasSuccessful() is not True:
            raise SystemExit(int(bool(result.errors or result.failures)))

cmdclasses['test'] = Tester

setup(name='django-scrypt',
      version=__version__,
      description='A Scrypt-enabled password hasher for Django 1.4/1.5',
      long_description=long_description,
      keywords=['Py-Scrypt', 'Scrypt', 'Django', 'Django-Scrypt'],
      author='Kelvin Wong',
      author_email='code@kelvinwong.ca',
      url='https://bitbucket.org/kelvinwong_ca/django-scrypt',
      classifiers=['Development Status :: 3 - Alpha',
                   'Framework :: Django',
                   'Intended Audience :: Developers',
                   'License :: OSI Approved :: BSD License',
                   'Programming Language :: Python :: 2.6',
                   'Programming Language :: Python :: 2.7',
                   'Programming Language :: Python :: 3.2',
                   'Programming Language :: Python :: 3.3',
                   'Topic :: Security :: Cryptography',
                   'Topic :: Software Development :: Libraries'],
      packages=['django_scrypt'],
      cmdclass=cmdclasses)
