import sys
import os
import fudge
import requests

sys.path.insert(0, os.path.abspath('..'))
from flyingsphinx import API, __version__

@fudge.patch('requests.get')
def test_get(get_method):
  response = fudge.Fake('Response')
  response.json = {'qux': 'quux'}

  get_method.expects_call().with_args(
    'https://flying-sphinx.com/api/my/app/path',
    params = {'id': '55'}, headers = {
      'Accept':                  'application/vnd.flying-sphinx-v3+json',
      'X-Flying-Sphinx-Token':   'abc:123',
      'X-Flying-Sphinx-Version': ('%s+python' % __version__)
    }
  ).returns(response)

  api = API('abc', '123')
  api.get('path', {'id': '55'})

@fudge.patch('requests.get')
def test_get_response(get_method):
  response = fudge.Fake('Response')
  response.json = {'qux': 'quux'}
  get_method.is_callable().calls(lambda uri, **kwargs: response)

  api = API('abc', '123')

  assert api.get('path') == {'qux': 'quux'}

@fudge.patch('requests.post')
def test_post(post_method):
  response = fudge.Fake('Response')
  response.json = {'qux': 'quux'}

  post_method.expects_call().with_args(
    'https://flying-sphinx.com/api/my/app/start', {}, headers = {
      'Accept':                  'application/vnd.flying-sphinx-v3+json',
      'X-Flying-Sphinx-Token':   'abc:123',
      'X-Flying-Sphinx-Version': ('%s+python' % __version__)
    }
  ).returns(response)

  api = API('abc', '123')
  api.post('start')

@fudge.patch('requests.post')
def test_post_response(post_method):
  response = fudge.Fake('Response')
  response.json = {'qux': 'quux'}
  post_method.is_callable().calls(lambda uri, params, **kwargs: response)

  api = API('abc', '123')

  assert api.post('path') == {'qux': 'quux'}

@fudge.patch('requests.put')
def test_put(put_method):
  response = fudge.Fake('Response')
  response.json = {'qux': 'quux'}

  put_method.expects_call().with_args(
    'https://flying-sphinx.com/api/my/app/path', {'foo': 'bar'}, headers = {
      'Accept':                  'application/vnd.flying-sphinx-v3+json',
      'X-Flying-Sphinx-Token':   'abc:123',
      'X-Flying-Sphinx-Version': ('%s+python' % __version__)
    }
  ).returns(response)

  api = API('abc', '123')
  api.put('path', {'foo': 'bar'})

@fudge.patch('requests.put')
def test_put_response(put_method):
  response = fudge.Fake('Response')
  response.json = {'qux': 'quux'}
  put_method.is_callable().calls(lambda uri, params, **kwargs: response)

  api = API('abc', '123')

  assert api.put('path') == {'qux': 'quux'}
