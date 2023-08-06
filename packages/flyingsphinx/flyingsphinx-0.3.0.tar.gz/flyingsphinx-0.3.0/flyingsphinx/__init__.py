"""
flyingsphinx
~~~~~~~~~~~~

:copyright: (c) 2012 by Pat Allan
:license: MIT, see LICENCE for more details.
"""

__title__     = 'flyingsphinx'
__version__   = '0.1.0'
__author__    = 'Pat Allan'
__license__   = 'MIT'
__copyright__ = 'Copyright 2012 Pat Allan'

from .api           import API
from .cli           import CLI
from .configuration import Configuration
from .index         import Index
from .sphinx        import Sphinx

def cli():
  import sys
  CLI(sys.argv[1], sys.argv[2:])

def configuration():
  return Configuration(API())

def index():
  return Index(API())

def info():
  return API().get('/')

def sphinx():
  return Sphinx(API())
