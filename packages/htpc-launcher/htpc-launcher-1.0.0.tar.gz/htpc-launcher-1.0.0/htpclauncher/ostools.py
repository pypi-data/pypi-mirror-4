import logging
import subprocess

class OsTools:
  def __init__(self):
    self.log = logging.getLogger('os')

  def runProcess(self, command):
    self.log.info('Running process: %s', command)
    return subprocess.Popen(command, shell = True)

  def findPid(self, regex):
    self.log.debug('Searching for Process with regex: %s', regex)
    findProc = subprocess.Popen('ps -ef | grep -P "%s" | grep -v grep' % regex, shell = True, stdout = subprocess.PIPE)
    findOut = findProc.communicate()[0]
    if not findOut:
      return None

    self.log.debug('Found proccess: %s', findOut)
    return findOut.split()[1]

  def terminate(self, pid):
    self.log.debug('Terminating pid %s', str(pid))
    subprocess.call('kill %s' % str(pid), shell = True)

  def kill(self, pid):
    self.log.debug('Killing pid %s', str(pid))
    subprocess.call('kill -9 %s' % str(pid), shell = True)

  def focus(self, process):
    self.log.info('Setting focus to %s' % process)
    subprocess.call('wmctrl -a %s' % process, shell = True)

  def doesWindowExist(self, window):
    try:
      # grep will have an exit status of 1 if no rows are found, which leads check_output to raise an error
      subprocess.check_output("wmctrl -l|grep -i %s" % window, shell=True)
      return True
    except:
      return False
