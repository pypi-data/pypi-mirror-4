import sys
import os
import fudge

sys.path.insert(0, os.path.abspath('..'))
from flyingsphinx import Configuration

@fudge.test
def test_configuration_upload():
  api = fudge.Fake('API')
  api.expects('put').with_args('/', {
    'configuration': 'provided content',
    'sphinx_version': '2.0.4'
  })
  Configuration(api).upload('provided content')

@fudge.patch('__builtin__.open')
def test_configuration_upload_from_file(fake_open):
  api       = fudge.Fake('API')
  conf_file = fudge.Fake('File')
  fake_open.is_callable().calls(lambda path: conf_file)
  conf_file.provides('read').returns('content in file')

  api.expects('put').with_args('/', {
    'configuration': 'content in file',
    'sphinx_version': '2.0.4'
  })

  Configuration(api).upload_from_file('/path/to/file')

@fudge.test
def test_settings_upload():
  api = fudge.Fake('API')

  api.expects('post').with_args('/add_file',
    {'setting': 'wordforms', 'file_name': 'foo.txt', 'content': 'contents'})

  Configuration(api).upload_settings('wordforms', 'foo.txt', 'contents')

@fudge.patch('__builtin__.open')
def test_settings_upload_from_file(fake_open):
  api       = fudge.Fake('API')
  conf_file = fudge.Fake('File')
  fake_open.is_callable().calls(lambda path: conf_file)
  conf_file.provides('read').returns('contents')
  conf_file.name = '/path/to/foo.txt'

  api.expects('post').with_args('/add_file',
    {'setting': 'wordforms', 'file_name': 'foo.txt', 'content': 'contents'})

  Configuration(api).upload_settings_from_file('wordforms', '/path/to/foo.txt')
