# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------
# note: $Id: note.py 44 2012-08-12 15:59:12Z griff1n $
# auth: griffin <griffin@uberdev.org>
# date: 2012/05/20
# copy: (C) CopyLoose 2012 UberDev <hardcore@uberdev.org>, No Rights Reserved.
#------------------------------------------------------------------------------

'''
The ``pysyncml.agents.note`` module provides helper routines and classes to
deal with SyncML note and memo object types.
'''

from . import base
from .. import constants, ctype
from ..items.note import NoteItem

#------------------------------------------------------------------------------
class BaseNoteAgent(base.Agent):

  #----------------------------------------------------------------------------
  def __init__(self, *args, **kw):
    super(BaseNoteAgent, self).__init__(*args, **kw)
    self.contentTypes = [
      ctype.ContentTypeInfo(constants.TYPE_SIF_NOTE, '1.1', preferred=True),
      ctype.ContentTypeInfo(constants.TYPE_SIF_NOTE, '1.0'),
      ctype.ContentTypeInfo(constants.TYPE_TEXT_PLAIN, ['1.1', '1.0']),
      ]

  #----------------------------------------------------------------------------
  def loadItem(self, stream, contentType=None, version=None):
    return NoteItem.load(stream, contentType, version)

  #----------------------------------------------------------------------------
  def dumpItem(self, item, stream, contentType=None, version=None):
    # todo: is this "getItem" really necessary?... it is for paranoia
    #       purposes to ensure that the object is actually a NoteItem.
    return self.getItem(item.id).dump(stream, contentType, version)

#------------------------------------------------------------------------------
# end of $Id: note.py 44 2012-08-12 15:59:12Z griff1n $
#------------------------------------------------------------------------------
