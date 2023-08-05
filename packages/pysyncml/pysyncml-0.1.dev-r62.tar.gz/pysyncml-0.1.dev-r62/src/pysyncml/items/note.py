# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------
# note: $Id: note.py 57 2012-09-04 00:16:40Z griff1n $
# lib:  pysyncml.items.note
# auth: griffin <griffin@uberdev.org>
# date: 2012/05/13
# copy: (C) CopyLoose 2012 UberDev <hardcore@uberdev.org>, No Rights Reserved.
#------------------------------------------------------------------------------

'''
The ``pysyncml.items.note`` module defines the abstract interface to a
Note object via the :class:`pysyncml.NoteItem
<pysyncml.items.note.NoteItem>` class.

.. warning::

  Be aware that this is NOT an object type defined by the SyncML
  specification, but rather is a *de-facto* standard object type.
'''

import os, re
import xml.etree.ElementTree as ET
from .base import Item, Ext
from .. import constants, common

#------------------------------------------------------------------------------
class NoteItem(Item, Ext):
  '''
  The NoteItem is an abstract sub-class of a :class:`pysyncml.Item
  <pysyncml.items.base.Item>` which primarily defines a "Note" as
  having a `name` and a `body`. It also provides implementations of
  the :meth:`dump` and :meth:`load` methods, which support the following
  content-types:

    * text/plain
    * text/x-s4j-sifn, version 1.1

  .. warning::

    The ``text/plain`` content-type does NOT support the `name` attribute,
    and therefore does not get synchronized when using that content-type.
  '''

  #----------------------------------------------------------------------------
  def __init__(self, name=None, body=None, *args, **kw):
    '''
    NoteItem constructor which takes attributes `name` and `body`.
    '''
    super(NoteItem, self).__init__(*args, **kw)
    self.name        = name
    self.body        = body

  #----------------------------------------------------------------------------
  def dump(self, stream, contentType=None, version=None):
    '''
    Serializes this NoteItem to a byte-stream and writes it to the
    file-like object `stream`. `contentType` and `version` must be one
    of the supported content-types, and if not specified, will default
    to ``text/plain``.
    '''
    if contentType is None or contentType == constants.TYPE_TEXT_PLAIN:
      stream.write(self.body)
      return
    if contentType == constants.TYPE_SIF_NOTE:
      root = ET.Element('note')
      # TODO: check `version`...
      ET.SubElement(root, 'SIFVersion').text = '1.1'
      if self.name is not None:
        ET.SubElement(root, 'Subject').text = self.name
      if self.body is not None:
        ET.SubElement(root, 'Body').text = self.body
      for name, values in self.extensions.items():
        for value in values:
          ET.SubElement(root, name).text = value
      ET.ElementTree(root).write(stream)
      return
    raise common.InvalidContentType('cannot serialize NoteItem to "%s"' % (contentType,))

  #----------------------------------------------------------------------------
  @classmethod
  def load(cls, stream, contentType=None, version=None):
    '''
    Reverses the effects of the :meth:`dump` method, creating a NoteItem
    from the specified file-like `stream` object.
    '''
    if contentType is None or contentType == constants.TYPE_TEXT_PLAIN:
      data = stream.read()
      name = data.split('\n')[0]
      # todo: localize?!...
      name = re.compile(r'^(title|name):\s*', re.IGNORECASE).sub('', name).strip()
      return NoteItem(name=name, body=data)
    if contentType == constants.TYPE_SIF_NOTE:
      data = ET.parse(stream).getroot()
      ret = NoteItem(name=data.findtext('Subject'), body=data.findtext('Body'))
      for child in data:
        if child.tag in ('SIFVersion', 'Subject', 'Body'):
          continue
        ret.addExtension(child.tag, child.text)
      return ret
    raise common.InvalidContentType('cannot de-serialize NoteItem from "%s"' % (contentType,))

  #----------------------------------------------------------------------------
  def __eq__(self, other):
    return self.name == other.name and self.body == other.body

#------------------------------------------------------------------------------
# end of $Id: note.py 57 2012-09-04 00:16:40Z griff1n $
#------------------------------------------------------------------------------
