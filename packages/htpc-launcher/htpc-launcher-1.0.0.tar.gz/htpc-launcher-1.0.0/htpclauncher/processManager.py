import logging

class ProcessManager:
  def __init__(self):
    self.log = logging.getLogger('ProcessManager')
    self.lastCommand = None

  def execute(self, command):
    if self._isNewCommand(command):
      self._stopAndClearLastCommand()

    self._runAndSetCommand(command)

  def _stopAndClearLastCommand(self):
    self.lastCommand.stop()
    self.lastCommand = None

  def _runAndSetCommand(self, command):
    try:
      command.run()
      self.lastCommand = command
    except:
      self.log.error('Failed to run %s', command)

  def _isNewCommand(self, command):
   return (self.lastCommand is not None) and (self.lastCommand != command)

