#!/usr/bin/env python
# Setup script for django-couchdb-utils

from distutils.core import setup

import re

src_main = open('django_couchdb_utils/__init__.py').read()
metadata = dict(re.findall("__([a-z]+)__ = '([^']+)'", src_main))
docstrings = re.findall('"""(.*?)"""', src_main, re.DOTALL)

# How is the package going to be called?
PACKAGE = 'django_couchdb_utils'

# List the modules that need to be installed/packaged
PACKAGES = (
        'django_couchdb_utils',
        'django_couchdb_utils.auth',
        'django_couchdb_utils.cache',
        'django_couchdb_utils.email',
        'django_couchdb_utils.openid_consumer',
        'django_couchdb_utils.sessions',
        'django_couchdb_utils.sessions.management',
        'django_couchdb_utils.sessions.management.commands',
        'django_couchdb_utils.test',
        'django_couchdb_utils.registration',
        'django_couchdb_utils.registration.management',
        'django_couchdb_utils.registration.management.commands',
        'django_couchdb_utils.registration.backends',
        'django_couchdb_utils.registration.backends.default',
        'django_couchdb_utils.registration.backends.simple',
)

PACKAGE_DATA = {}
for package in PACKAGES:
    PACKAGE_DATA[package] = ['_design/views/*/*.js']


# Metadata fields extracted from the main file
AUTHOR_EMAIL = metadata['author']
VERSION = metadata['version']
WEBSITE = metadata['website']
LICENSE = metadata['license']
DESCRIPTION = docstrings[0]

# Extract name and e-mail ("Firstname Lastname <mail@example.org>")
AUTHOR, EMAIL = re.match(r'(.*) <(.*)>', AUTHOR_EMAIL).groups()

setup(name=PACKAGE,
      version=VERSION,
      description=DESCRIPTION,
      author=AUTHOR,
      author_email=EMAIL,
      license=LICENSE,
      url=WEBSITE,
      packages=PACKAGES,
      package_data=PACKAGE_DATA,
      download_url='http://pypi.python.org/packages/source/' + \
              PACKAGE[0] + '/' + PACKAGE + \
              '/'+PACKAGE+'-'+VERSION+'.tar.gz')
