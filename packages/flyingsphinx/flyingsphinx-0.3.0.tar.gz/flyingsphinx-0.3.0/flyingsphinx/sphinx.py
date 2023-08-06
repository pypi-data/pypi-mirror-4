class Sphinx(object):
  def __init__(self, api):
    self.api = api

  def start(self):
    self.api.post('start')

  def stop(self):
    self.api.post('stop')
