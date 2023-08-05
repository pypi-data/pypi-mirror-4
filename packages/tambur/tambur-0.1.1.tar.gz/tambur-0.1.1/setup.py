#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name = 'tambur',
    version = '0.1.1',
    description = 'Tambur.io Client',
    author = 'Andre Graf',
    author_email = 'graf@tambur.io',
    url = 'http://github.com/tamburio/python-tambur',
    packages = find_packages(),
    install_requires = ['requests==0.13.0'],
    classifiers = [
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
