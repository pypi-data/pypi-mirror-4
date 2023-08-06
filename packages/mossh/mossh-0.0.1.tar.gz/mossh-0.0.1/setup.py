#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-

from setuptools import setup, find_packages

setup(
    name = 'mossh',
    version = '0.0.1',
    packages = ["mossh"],
    author = 'Rob McQueen',
    author_email = 'rob@systemizer.me',
    description = 'An easier way to ssh into your chef servers',
    license = 'Apache 2.0',
    keywords = '',
    url = 'http://github.com/mopub/mossh',
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
    install_requires = [
        "PyChef==0.2.1",
        ],
    entry_points={
        "console_scripts" : [
            'mossh = mossh:run'
            ]
        }
)
