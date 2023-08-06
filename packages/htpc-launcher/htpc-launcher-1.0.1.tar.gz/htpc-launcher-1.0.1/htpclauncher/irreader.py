import logging
from socketreader import SocketReader

class IrReaderError(Exception):
  pass

class IrReader:
  def __init__(self, socketReader = None):
    self.log = logging.getLogger('IrReader')
    self.socketReader = socketReader
    if not self.socketReader:
      self.socketReader = SocketReader('/var/run/lirc/lircd')
    self.streamBuffer = ''

  def getNextCode(self):
    while True:
      self._connectLirc()
      self._readFromLirc()
      message = self._getNextMessage()
      if not message:
        continue

      code = self._getKeyNameFromMessage(message)
      if not code:
        continue
      return code

  def _getKeyNameFromMessage(self, message):
    if not message:
      return None

    # from http://lirc.org/html/technical.html#applications
    # format of an lircd message is: <code> <repeat count> <button name> <remote control name>
    (code, repeatCount, buttonName, remoteName) = message.split()
    if int(repeatCount, 16) > 0:
      return None
    return buttonName

  def _connectLirc(self):
    self.socketReader.connect()
    if not self.socketReader.isConnected():
      raise IrReaderError()

  def _readFromLirc(self):
    incoming = self.socketReader.read()
    if incoming is None:
      raise IrReaderError()
    self.streamBuffer += incoming

  def _getNextMessage(self):
    newlinePosition = self.streamBuffer.find('\n')
    if newlinePosition == -1:
      return None
    message = self.streamBuffer[:newlinePosition]
    self.streamBuffer = self.streamBuffer[newlinePosition + 1:]

    self.log.debug('Read message from lircd: %s', message.strip())
    return message

