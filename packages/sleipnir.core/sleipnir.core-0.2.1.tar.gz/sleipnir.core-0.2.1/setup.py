#!/usr/bin/env python
# -*- mode: Python; indent-tabs-mode: nil; coding: utf-8  -*-

#
# Copyright 2010, 2011 Carlos Martín
# Copyright 2010, 2011 Universidad de Salamanca
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.

"""Main Setup File"""

import os
import re
import sys

if sys.version_info < (2, 6):
    sys.stderr.write("Sleipnir requires Python 2.6 or higher.")
    sys.exit(0)

# Load constants
sys.path.insert(0, os.path.dirname(__file__) + os.sep + 'src')
from pkg_resources import fixup_namespace_packages
fixup_namespace_packages(sys.path[0])

# setuptools build required.
from setuptools import setup, find_packages
from sleipnir.core import constants

# Peek author details
AUTHOR, EMAIL = re.match(r'^(.*) <(.*)>$', constants.__author__).groups()

setup(
    author             = AUTHOR,
    author_email       = EMAIL,
    classifiers        = constants.__classifiers__,
    description        = constants.__summary__,
    install_requires   = constants.__requires__,
    license            = constants.__license__,
    long_description   = constants.__long_description__,
    name               = constants.__appname__,
    namespace_packages = [constants.__namespace__],
    package_dir        = {'': 'src'},
    packages           = find_packages(where=sys.path[0], exclude=['*.tests']),
    test_suite         = constants.__appname__ + '.tests',
    tests_require      = [constants.__tests_requires__],
    url                = constants.__url__,
    version            = constants.__version__,
    zip_safe           = False,
)
