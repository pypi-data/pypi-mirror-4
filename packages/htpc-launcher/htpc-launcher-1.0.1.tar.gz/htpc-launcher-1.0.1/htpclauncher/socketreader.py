import socket, logging
from select import select

class SocketReader:
  def __init__(self, address):
    self.log = logging.getLogger('SocketReader')
    self.address = address
    self.socket = None

  def isConnected(self):
    return self.socket is not None

  def connect(self):
    if self.socket is not None:
      return
    self.socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    try:
      self.socket.connect(self.address)
    except socket.error:
      self.log.error('Failed to connect to %s', self.address)
      self.disconnect()
      return
    select([], [self.socket], [])
    self.log.debug('Conencted to %s', self.address)

  def read(self):
    readable, writable, exception = select([self.socket], [], [])
    data = self.socket.recv(1024)
    if not data:
      self.log.debug('Socket connection terminated')
      self.disconnect()
      return None
    return data

  def disconnect(self):
    if not self.socket:
      return
    self.socket.close()
    self.socket = None

