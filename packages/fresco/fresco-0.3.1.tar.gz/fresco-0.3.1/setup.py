#!/usr/bin/env python
# Copyright (c) 2007-2011 Oliver Cope. All rights reserved.
# See LICENSE.txt for terms of redistribution and use.

import os
import re
from setuptools import setup, find_packages

VERSIONFILE = "fresco/__init__.py"


def get_version():
    with open(VERSIONFILE, 'rb') as f:
        return re.search("^__version__\s*=\s*['\"]([^'\"]*)['\"]",
                           f.read().decode('UTF-8'), re.M).group(1)


def read(*path):
    """
    Return content from ``path`` as a string
    """
    with open(os.path.join(os.path.dirname(__file__), *path), 'rb') as f:
        return f.read().decode('UTF-8')

setup(
    name='fresco',
    version=get_version(),
    description='A web micro-framework',
    long_description=read('README.txt') + "\n\n" + read("CHANGELOG.txt"),
    author='Oliver Cope',
    license='BSD',
    author_email='oliver@redgecko.org',
    url='http://www.ollycope.com/software/fresco',
    zip_safe=False,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Internet :: WWW/HTTP :: WSGI',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    install_requires=['blinker']
)
