import time
from htpclauncher.config import Config
import os, logging, logging.handlers
from irreader import IrReader, IrReaderError
from processManager import ProcessManager

from . import DEFAULT_CONF_FILE, DEFAULT_LOG_FILE

class IrSwitchApp:
  def __init__(self):
    self.startLogging()

    self.config = Config()
    self.config.load(open(os.path.expanduser(DEFAULT_CONF_FILE)))

    self.irReader = IrReader()
    self.processManager = ProcessManager()

  def run(self):
    try:
      self._processIrCode(self.config.getLaunchCommand())

      while True:
        try:
          try:
            code = self.irReader.getNextCode()
          except IrReaderError:
            time.sleep(5)
            continue
          self._processIrCode(code)
        except KeyboardInterrupt:
          break
    except:
      self.log.exception('Unhandled exception')

  def startFileLogging(self):
    formatter = logging.Formatter('%(asctime)s %(levelname)s - %(message)s')
    filePath = os.path.expanduser(DEFAULT_LOG_FILE)

    handler = logging.handlers.RotatingFileHandler(filePath, maxBytes = 1024000, backupCount = 5)
    handler.setFormatter(formatter)
    self.log.addHandler(handler)

  def startStreamLogging(self):
    formatter = logging.Formatter('%(asctime)s %(levelname)s - %(message)s')
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    self.log.addHandler(handler)

  def startLogging(self):
    self.log = logging.getLogger()
    self.log.setLevel(logging.DEBUG)

    self.startStreamLogging()
    self.startFileLogging()

  def _processIrCode(self, code):
    command = self.config.getCommand(code)
    if not command:
      return
    self.processManager.execute(command)

def main():
  IrSwitchApp().run()

