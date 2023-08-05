from sys import stdout
import time

class Index(object):
  def __init__(self, api):
    self.api = api

  def run(self, indices = []):
    id = self.api.post('indices', {'indices': ','.join(indices)})['id']

    result = self.api.get(('indices/%s' % id))
    while result['status'] == 'PENDING':
      time.sleep(3)
      result = self.api.get(('indices/%s' % id))

    if result['status'] == 'FAILED':
      stdout.write('Index request failed.\n')
    else:
      stdout.write('%s\n' % result['log'])

  def last(self):
    result = self.api.get('indices/last')
    stdout.write('%s\n' % result['log'])
