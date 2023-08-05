import sys
import os
import fudge

sys.path.insert(0, os.path.abspath('..'))
from flyingsphinx import Index

@fudge.test
def test_index_start():
  api = fudge.Fake('API')
  api.provides('get').returns({'status': 'FINISHED', 'log': 'indexer output'})

  api.expects('post').with_args('indices', {'indices': ''})\
    .returns({'id': '55'})

  Index(api).run()

@fudge.test
def test_index_checks():
  api = fudge.Fake('API')
  api.provides('post').returns({'id': '55'})

  api.expects('get').with_args('indices/55').returns({
    'status': 'FINISHED',
    'log':    'indexer output'
  })

  Index(api).run()

@fudge.patch('time.sleep')
def test_index_checks_more_than_once(sleep):
  api = fudge.Fake('API')
  api.provides('post').returns({'id': '55'})
  api.provides('get').with_args('indices/55').returns({'status': 'PENDING'})\
    .next_call().returns({'status': 'FINISHED', 'log': 'indexer output'})

  sleep.expects_call().with_args(3)

  Index(api).run()

@fudge.patch('sys.stdout.write')
def test_index_prints_result(printer):
  api = fudge.Fake('API')
  api.provides('post').returns({'id': '55'})
  api.provides('get').with_args('indices/55').returns({
    'status': 'FINISHED',
    'log':    'indexer output'
  })

  printer.expects_call().with_args('indexer output\n')

  Index(api).run()

@fudge.patch('sys.stdout.write')
def test_index_prints_result(printer):
  api = fudge.Fake('API')
  api.provides('post').returns({'id': '55'})
  api.provides('get').with_args('indices/55').returns({'status': 'FAILED'})

  printer.expects_call().with_args('Index request failed.\n')

  Index(api).run()

@fudge.patch('sys.stdout.write')
def test_last_index_prints_result(printer):
  api = fudge.Fake('API')
  api.provides('get').with_args('indices/last').returns({
    'status': 'FINISHED',
    'log':    'indexer output'
  })

  printer.expects_call().with_args('indexer output\n')

  Index(api).last()