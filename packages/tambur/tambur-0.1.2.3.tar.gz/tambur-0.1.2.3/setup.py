#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name = 'tambur',
    version = '0.1.2.3',
    description = 'Tambur.io Client',
    author = 'Andre Graf',
    author_email = 'graf@tambur.io',
    url = 'http://github.com/tamburio/python-tambur',
    packages = find_packages(),
    install_requires = [
        'requests-oauthlib>=0.2.0',
        'requests>=1.1.0' # would be resolved by requests-oauthlib however this would pull in the old pypi-version
    ],
    dependency_links = [
        'https://github.com/kennethreitz/requests/tarball/master#egg=requests-1.1.0',
        'https://github.com/requests/requests-oauthlib/tarball/master#egg=requests-oauthlib-0.2.0'
    ],
    classifiers = [
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
