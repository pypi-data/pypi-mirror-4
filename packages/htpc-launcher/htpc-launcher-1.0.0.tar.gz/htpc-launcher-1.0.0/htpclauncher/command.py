import logging, time
from ostools import OsTools

DEFAULT_COMMAND_TIMEOUT = 3

class CommandError(Exception):
  pass

class Command:
  def __init__(self, process, search = None, needsKill = False, startTimeout = DEFAULT_COMMAND_TIMEOUT, ostools = None):
    self.log = logging.getLogger('Command')
    self.process = process
    self.needsKill = needsKill
    self.startTimeout = startTimeout

    self.ostools = ostools
    if not self.ostools:
      self.ostools = OsTools()

    self.search = search
    if not self.search:
      self.search = self.process

  def __str__(self):
    return self.process

  def __eq__(self, other):
    return self.process == other.process

  def __ne__(self, other):
    return not self == other

  def run(self):
    if self.isRunning():
      if self.ostools.doesWindowExist(self.process):
        self.log.debug('%s already running, setting focus', self)
        self.ostools.focus(self.process)
        return
      else:
        self.log.debug('%s is already running, but has no window; restarting process', self)
        self.stop()

    self.log.info('Running %s', self)
    self.ostools.runProcess(self.process)
    self._waitForProcess()

  def stop(self):
    pid = self.ostools.findPid(self.search)
    if not pid:
      return

    self.log.info('Stopping %s', self)
    if self.needsKill:
      self.ostools.kill(pid)
    else:
      self.ostools.terminate(pid)

  def isRunning(self):
    pid = self.ostools.findPid(self.search)
    return pid is not None

  def _waitForProcess(self):
    self.log.debug('Waiting for %s', self)
    start = time.time()
    while not self.isRunning():
      time.sleep(0.5)
      if (time.time() - start) > self.startTimeout:
        raise CommandError()

