#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys

from setuptools import setup, find_packages
import airstrip

if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    sys.exit()

os.environ['PYTHONDONTWRITEBYTECODE'] = '1'

requires = [
    'puke',
    'verlib'
]

setup(
    name='AirStrip',
    version=airstrip.__version__,
    description='Third-party js dependencies manager',
    long_description=open('README.md').read(),
    author='WebItUp',
    author_email='tech@webitup.fr',
    url='http://airstrip.jsboot.com/',
    packages=find_packages(),
    scripts=[
        'airstrip/bin/airstrip'
    ],
    package_dir={'airstrip': 'airstrip'},
    package_data = {
        # If any package contains *.txt files, include them:
        '': ['*.json']
    },
    include_package_data = True,

    install_requires=requires,
    license=open('LICENSE.md').read()
)
