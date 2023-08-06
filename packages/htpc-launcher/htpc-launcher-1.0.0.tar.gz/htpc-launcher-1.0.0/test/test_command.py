import threading
import time
from htpclauncher.command import Command, CommandError
from htpclauncher.ostools import OsTools
from mock import Mock
import pytest

class TestCommand:
  def setup_method(self, method):
    self.ostools = Mock(OsTools)
    self.pid = '1234'
    self.ostools.findPid.return_value = self.pid
    self.command = Command('something', search = 'whatever', ostools = self.ostools)

  def testCommandIsRun(self):
    self.ostools.findPid.return_value = None
    run = threading.Thread(target = self.command.run)
    run.start()
    time.sleep(0.1)
    self.ostools.findPid.return_value = 123
    run.join()

    self.ostools.runProcess.assert_called_with('something')

  def testPidIsKilledWhenStopped(self):
    self.command.stop()
    self.ostools.terminate.assert_called_with(self.pid)

  def testNothingKilledWhenPreviousProcessNotRunning(self):
    self.ostools.findPid.return_value = None
    self.command.stop()
    assert not self.ostools.terminate.called
    assert not self.ostools.kill.called

  def testNothingStartedWhenProcessAlreadyRunning(self):
    self.ostools.findPid.return_value = self.pid
    self.command.run()
    assert not self.ostools.runProcess.called

  def testCommandTerminatedWithSigKillIfOptionSet(self):
    self.command.needsKill = True
    self.command.stop()
    self.ostools.kill.assert_called_with(self.pid)

  def testFocusCalledWhenProcessAlreadyRunning(self):
    self.ostools.findPid.return_value = self.pid
    self.ostools.doesWindowExist('something').return_value = True
    self.command.run()
    assert self.ostools.focus.called

  def testCommandErrorRaisedIfProgramFailsToStart(self):
    self.command.startTimeout = 0
    self.ostools.findPid.return_value = None
    with pytest.raises(CommandError):
      self.command.run()

  def testCheckForWindowIsCalledIfProcessIsRunning(self):
    self.ostools.findPid.return_value = self.pid
    self.command.run()
    self.ostools.doesWindowExist.assert_called_with('something')

  def testCommandTerminatedIfNoWindowExists(self):
    self.ostools.findPid.return_value = self.pid
    self.ostools.doesWindowExist.return_value = False
    self.command.run()
    assert self.ostools.terminate.called

  def testCommandStartedIfNoWindowExists(self):
    self.ostools.findPid.return_value = self.pid
    self.ostools.doesWindowExist.return_value = False
    run = threading.Thread(target = self.command.run)
    run.start()
    time.sleep(0.1)
    run.join()
    self.ostools.runProcess.assert_called_with('something')

