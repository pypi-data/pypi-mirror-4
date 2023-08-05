import requests
import os
import re
import flyingsphinx

class API(object):
  URI_BASE   = 'https://flying-sphinx.com/api/my/app'
  API_ACCEPT = 'application/vnd.flying-sphinx-v3+json'

  def __init__(self, identifier = None, api_key = None):
    self.identifier = identifier or os.environ['FLYING_SPHINX_IDENTIFIER']
    self.api_key    = api_key    or os.environ['FLYING_SPHINX_API_KEY']

  def get(self, path, body={}):
    return requests.get(self._normalised_uri(path), params = body,
      headers = self._headers()).json

  def post(self, path, body={}):
    return requests.post(self._normalised_uri(path), body,
      headers = self._headers()).json

  def put(self, path, body={}):
    return requests.put(self._normalised_uri(path), body,
      headers = self._headers()).json

  def _headers(self):
    return {
      'Accept':                  API.API_ACCEPT,
      'X-Flying-Sphinx-Token':   ('%s:%s' % (self.identifier, self.api_key)),
      'X-Flying-Sphinx-Version': ('%s+python' % flyingsphinx.__version__)
    }

  def _normalised_uri(self, path):
    path = '' if (path == '/') else ('/%s' % re.sub(r"^/", '', path))

    return API.URI_BASE + path
