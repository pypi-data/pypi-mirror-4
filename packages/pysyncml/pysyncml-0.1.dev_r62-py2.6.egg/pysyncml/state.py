# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------
# file: $Id: state.py 60 2012-09-16 20:37:30Z griff1n $
# lib:  pysyncml.state
# auth: griffin <griffin@uberdev.org>
# date: 2012/05/20
# copy: (C) CopyLoose 2012 UberDev <hardcore@uberdev.org>, No Rights Reserved.
#------------------------------------------------------------------------------

'''
The ``pysyncml.state`` is an internal package that abstracts SyncML
state related objects, including :class:`pysyncml.state.Session`,
:class:`pysyncml.state.Request` and
:class:`pysyncml.state.Command`.
'''

from .common import adict

#------------------------------------------------------------------------------
class Session(adict):
  '''
  Stores session state information for managing SyncML transactions.

  .. important::

    *IMPORTANT*: anything stored in this object MUST be serializable as it
    may be serialized by servers after closing a client connection!

  '''
  def __init__(self, *args, **kw):
    # note: overriding dict's init to set some default values
    self.id        = 1
    self.isServer  = True
    self.msgID     = 1
    self.cmdID     = 0
    self.dsstates  = dict()
    self.stats     = dict()
    super(Session, self).__init__(*args, **kw)
  @property
  def nextMsgID(self):
    # TODO: what if the session is in server mode... then the msgID is
    #       controlled by the client, right? and it may not be an int...
    self.msgID += 1
    self.cmdID = 0
    return self.msgID
  @property
  def nextCmdID(self):
    self.cmdID += 1
    return self.cmdID

#------------------------------------------------------------------------------
class Request(adict): pass
Response = Request

#------------------------------------------------------------------------------
class Command(adict):
  nonStringAttributes = ('data',)
  def __init__(self, **kw):
    # note: explicitly overriding dict's init behavior because Command does
    #       something special with attribute values (conditionally turns them
    #       into strings)
    for k, v in kw.items():
      setattr(self, k, v)
  def __setattr__(self, key, value):
    if value is None or key in Command.nonStringAttributes or key.startswith('_'):
      self[key] = value
    else:
      self[key] = str(value)
    return self

#------------------------------------------------------------------------------
class Stats(adict):
  def __init__(self, *args, **kw):
    # note: overriding dict's init to set some default values
    self.mode      = None
    self.hereAdd   = 0
    self.hereMod   = 0
    self.hereDel   = 0
    self.hereErr   = 0
    self.peerAdd   = 0
    self.peerMod   = 0
    self.peerDel   = 0
    self.peerErr   = 0
    self.conflicts = 0
    self.merged    = 0
    super(Stats, self).__init__(*args, **kw)

#------------------------------------------------------------------------------
# end of $Id: state.py 60 2012-09-16 20:37:30Z griff1n $
#------------------------------------------------------------------------------
