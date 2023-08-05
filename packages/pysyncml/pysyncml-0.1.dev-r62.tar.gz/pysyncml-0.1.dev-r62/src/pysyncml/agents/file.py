# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------
# file: $Id: file.py 44 2012-08-12 15:59:12Z griff1n $
# auth: griffin <griffin@uberdev.org>
# date: 2012/05/13
# copy: (C) CopyLoose 2012 UberDev <hardcore@uberdev.org>, No Rights Reserved.
#------------------------------------------------------------------------------

'''
The ``pysyncml.agents.file`` module provides helper routines and classes to
deal with SyncML file and folder object types.
'''

from . import base
from .. import constants, ctype
from ..items import FileItem, FolderItem

#------------------------------------------------------------------------------
class BaseFileAgent(base.Agent):

  #----------------------------------------------------------------------------
  def __init__(self, *args, **kw):
    super(BaseFileAgent, self).__init__(*args, **kw)
    self.hierarchicalSync = True
    self.contentTypes = [
      ctype.ContentTypeInfo(constants.TYPE_OMADS_FILE, '1.2', preferred=True),
      ctype.ContentTypeInfo(constants.TYPE_OMADS_FOLDER, '1.2'),
      ]

  #----------------------------------------------------------------------------
  def loadItem(self, stream, contentType=None, version=None):
    if contentType is not None:
      if ctype.getBaseType(contentType) == constants.TYPE_OMADS_FOLDER:
        return FolderItem.load(stream, contentType, version)
    return FileItem.load(stream, contentType, version)

  #----------------------------------------------------------------------------
  def dumpItem(self, item, stream, contentType=None, version=None):
    # todo: is this "getItem" really necessary?... it is for paranoia
    #       purposes to ensure that the object is actually a FileItem.
    item = self.getItem(item.id)
    if contentType is not None and \
       not ctype.getBaseType(contentType) == constants.TYPE_OMADS_FOLDER and \
       not ctype.getBaseType(contentType) == constants.TYPE_OMADS_FILE:
      raise common.InvalidContentType('cannot serialize file item to "%s"' % (contentType,))
    if isinstance(item, FolderItem):
      # todo: this is a bit of a hack... i'm not really sure how to
      #       resolve it. the rest of pysyncml is geared toward an agent
      #       only being able to handle a single content-type...
      return item.dump(stream, constants.TYPE_OMADS_FOLDER, version)
    return item.dump(stream, constants.TYPE_OMADS_FILE, version)

#------------------------------------------------------------------------------
# end of $Id: file.py 44 2012-08-12 15:59:12Z griff1n $
#------------------------------------------------------------------------------
