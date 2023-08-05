#!/usr/bin/env python

import os
import sys

from setuptools import setup

os.environ['PYTHONDONTWRITEBYTECODE'] = '1'

setup(
  name                 = 'flyingsphinx',
  version              = '0.2.1',
  description          = 'Flying Sphinx Python client',
  long_description     = 'Flying Sphinx API client for Python applications',
  author               = 'Pat Allan',
  author_email         = 'pat@freelancing-gods.com',
  url                  = 'https://github.com/flying-sphinx/flying-sphinx-py',
  packages             = ['flyingsphinx'],
  include_package_data = True,
  install_requires     = ['requests'],
  license              = open('LICENCE').read(),
  entry_points         = {
    'console_scripts': [
      'flying-sphinx = flyingsphinx:cli'
    ]
  },
  classifiers          = (
    'Development Status :: 3 - Alpha',
    'Intended Audience :: Developers',
    'Natural Language :: English',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python',
    'Programming Language :: Python :: 2.7'
  )
)
