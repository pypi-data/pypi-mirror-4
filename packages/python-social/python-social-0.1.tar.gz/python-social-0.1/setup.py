#!/usr/bin/env/python
# -*- coding: utf-8 -*-

import os

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name='python-social',
    version="0.1",
    url='https://github.com/aurorasoftware/python-social',
    license="",
    long_description="",
    description='Integrate with any third party, easily.',
    author="Dan Loewenherz",
    author_email="dan@dlo.me",
    packages=['social', 'social.facebook'],
)

