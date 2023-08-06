from StringIO import StringIO
from htpclauncher.config import Config

class TestConfig:
  def setup_method(self, method):
    self.contents = StringIO('''
[startup]
launch = LAUNCH_KEY
[KEY_NAME]
process = processName
search = searchString
needsKill = false
[KILL_NAME]
process = anotherProcessName
needsKill = true
    ''')
    self.config = Config()
    self.config.load(self.contents)

  def testCommandsLoadedWithCorrectProcess(self):
    assert self.config.getCommand('KEY_NAME').process == 'processName'

  def testCommandsLoadedWithCorrectSearchString(self):
    assert self.config.getCommand('KEY_NAME').search == 'searchString'

  def testCommandsLoadedWithCorrectKillFlagWhenFalse(self):
    assert self.config.getCommand('KEY_NAME').needsKill == False

  def testCommandsLoadedWithCorrectKillFlagWhenTrue(self):
    assert self.config.getCommand('KILL_NAME').needsKill == True

  def testAutoLaunchKeyIsLoaded(self):
    assert self.config.getLaunchCommand() == 'LAUNCH_KEY'

