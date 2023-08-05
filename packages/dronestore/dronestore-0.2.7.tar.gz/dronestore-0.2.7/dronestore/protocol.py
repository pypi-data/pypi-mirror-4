
from types import DictType
from types import StringType



class ProtocolError(Exception):
  __slots__ = ('kind', 'message')
  def __init__(self, call, message):
    self.kind = 'Protocol (%d)' % call
    self.message = message

class RPC(object):
  __slots__ = ('kind', 'args')

  def __repr__(self):
    return 'RPC %s (%s)' % (self.kind, str(self.args))

  def __str__(self):
    return 'RPC %s (%s)' % (self.kind, str(self.args))

  def handle(self):
    raise NotImplementedError('No implementation for RPC ')