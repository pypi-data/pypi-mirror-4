#!/usr/bin/env python2

import os
import sys

try:
    from distutils.core import setup, Extension, find_packages
except ImportError:
    from setuptools import setup, Extension, find_packages

# Publish Helper.
if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    sys.exit()

iwlib = Extension("iwlib.iwconfig",
        sources=["iwlib/iwconfig.c"],
        libraries=["iw"])

settings = {
    'name': 'iwlib',
    'version': '1.2.1',
    'description': "Python module to interface with iwlib",
    'long_description': open('README.rst').read(),
    'author': 'Nathan Hoad',
    'author_email': 'nathan@getoffmalawn.com',
    'url': 'https://bitbucket.org/getoffmalawn/python-iwlib',
    'license': 'GPLv2',
    'classifiers': (
        # 'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
    ),
    'ext_modules': [iwlib],
    'packages': find_packages(),
}

setup(**settings)
