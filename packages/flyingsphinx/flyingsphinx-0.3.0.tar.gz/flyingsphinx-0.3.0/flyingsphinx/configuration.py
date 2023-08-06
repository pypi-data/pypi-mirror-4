from os.path import basename

class Configuration(object):
  def __init__(self, api):
    self.api = api

  def upload(self, configuration):
    self.api.put('/', {
      'configuration': configuration,
      'sphinx_version': '2.0.4'
    })

  def upload_from_file(self, path):
    file = open(path)
    self.upload(file.read())

  def upload_settings(self, setting, name, contents):
    self.api.post('/add_file', {
      'setting':   setting,
      'file_name': name,
      'content':   contents
    })

  def upload_settings_from_file(self, setting, path):
    file = open(path)
    self.upload_settings(setting, basename(file.name), file.read())
