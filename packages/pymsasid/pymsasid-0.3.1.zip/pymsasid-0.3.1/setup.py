#!/usr/bin/env python

from distutils.core import setup

setup(
    provides     = ['pymsasid'],
    packages     = ['pymsasid'],
    name         = 'pymsasid',
    version      = '0.3.1',
    description  = 'A pure python disassembling library',
    url          = 'https://code.google.com/p/pymsasid/',
    download_url = 'https://pymsasid.googlecode.com/files/pymsasid-0.31.zip',
    classifiers  = [
                    'License :: OSI Approved :: BSD License',
                    'Development Status :: 4 - Beta',
                    'Programming Language :: Python :: 2',
                    ],
)
