from htpclauncher.command import Command, CommandError
from htpclauncher.processManager import ProcessManager
from mock import Mock

class TestProcessManager:
  def setup_method(self, method):
    self.command = Mock(Command)
    self.processManager = ProcessManager()

  def testCommandIsRunWhenExecuted(self):
    self.processManager.execute(self.command)
    assert self.command.run.called

  def testPreviousCommandIsStoppedWhenStartingNewCommand(self):
    self.processManager.execute(self.command)
    self.processManager.execute(Mock(Command))
    assert self.command.stop.called

  def testCommandIsNotStoppedIfSameAsPreviousCommand(self):
    self.processManager.execute(self.command)
    self.processManager.execute(self.command)
    assert not self.command.stop.called

  def testCommandIsRerunIfNotRunning(self):
    self.processManager.execute(self.command)
    self.command.isRunning.return_value = False
    self.processManager.execute(self.command)
    assert self.command.run.call_count == 2

  def testNoErrorRaisedIfCommandFailsToRun(self):
    self.command.run.side_effect = CommandError()
    self.processManager.execute(self.command)

