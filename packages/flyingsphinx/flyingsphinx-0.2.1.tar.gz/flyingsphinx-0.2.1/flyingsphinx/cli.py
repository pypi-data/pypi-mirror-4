import flyingsphinx

class CLI(object):
  def __init__(self, command, arguments):
    if command == 'configure':
      flyingsphinx.configuration().upload_from_file(arguments[0])
      print 'Sphinx configured'
    elif command == 'index':
      flyingsphinx.index().run()
    elif command == 'start':
      flyingsphinx.sphinx().start()
      print 'Sphinx started'
    elif command == 'stop':
      flyingsphinx.sphinx().stop()
      print 'Sphinx stopped'
    elif command == 'restart':
      flyingsphinx.sphinx().stop()
      print 'Sphinx stopped'
      flyingsphinx.sphinx().start()
      print 'Sphinx started'
    elif command == 'rebuild':
      flyingsphinx.sphinx().stop()
      print 'Sphinx stopped'
      flyingsphinx.index().run()
      flyingsphinx.sphinx().start()
      print 'Sphinx started'
    else:
      print 'Unknown command %s' % command
