from htpclauncher.irreader import IrReader, IrReaderError
from htpclauncher.socketreader import SocketReader
import pytest
from mock import Mock

class TestIrReader:
  def setup_method(self, method):
    self.keyName = 'KEY_SOMETHING'
    self.lircMessage = '0x12345678 0 %s REMOTE_NAME\n' % self.keyName

    self.socketReader = Mock(SocketReader)
    self.socketReader.read.return_value = self.lircMessage
    self.socketReader.isConnected.return_value = True

    self.reader = IrReader(self.socketReader)

  def testGettingCodeConnectsToSocket(self):
    self.reader.getNextCode()
    assert self.socketReader.connect.called

  def testGettingCodeReturnsCodeFromMessage(self):
    code = self.reader.getNextCode()
    assert code == self.keyName

  def testGettingCodeSkipsKeyRepeats(self):
    self.socketReader.read.return_value = '0x12345678 01 KEY_BAD REMOTE_NAME\n' + self.lircMessage

    code = self.reader.getNextCode()
    assert code == self.keyName

  def testIrReaderFailureRaisesException(self):
    self.socketReader.isConnected.return_value = False
    with pytest.raises(IrReaderError):
      self.reader.getNextCode()
