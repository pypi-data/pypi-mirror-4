#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-
import os

from setuptools import setup, find_packages

setup(
    name = 'cheffab',
    version = '0.0.1',
    packages = find_packages(),
    author = 'Rob McQueen',
    author_email = 'rob@mopub.com',
    description = 'Fabric wrapper for chef integration',
    license = 'Apache 2.0',
    keywords = '',
    url = 'http://github.com/mopub/cheffab',
    classifiers = [
        #'Development Status :: 1 - Planning',
        #'Development Status :: 2 - Pre-Alpha',
        'Development Status :: 3 - Alpha',
        #'Development Status :: 4 - Beta',
        #'Development Status :: 5 - Production/Stable',
        #'Development Status :: 6 - Mature',
        #'Development Status :: 7 - Inactive',
        "License :: OSI Approved :: Apache Software License",
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ],
    zip_safe = False,
    tests_require = ['unittest2', 'mock'],
    test_suite = 'unittest2.collector',
    install_requires = [
        "Fabric==1.6.0",
        "PyChef==0.2.1",
        "requests==1.2.0",
        ]
)
