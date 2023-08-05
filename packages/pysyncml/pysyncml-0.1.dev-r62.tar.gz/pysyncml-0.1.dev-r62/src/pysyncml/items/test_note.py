# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------
# file: $Id: test_note.py 23 2012-06-03 19:23:36Z griff1n $
# lib:  pysyncml.items.test_note
# auth: griffin <griffin@uberdev.org>
# date: 2012/06/03
# copy: (C) CopyLoose 2012 UberDev <hardcore@uberdev.org>, No Rights Reserved.
#------------------------------------------------------------------------------

import unittest, logging
from .note import NoteItem
from .. import constants, common

# kill logging
logging.disable(logging.CRITICAL)

#------------------------------------------------------------------------------
class TestNote(unittest.TestCase):

  #----------------------------------------------------------------------------
  def test_plain_load(self):
    note = NoteItem.loads('content', contentType=constants.TYPE_TEXT_PLAIN)
    self.assertEqual('content', note.name)
    self.assertEqual('content', note.body)

  #----------------------------------------------------------------------------
  def test_plain_dump(self):
    note = NoteItem(name='this note name', body='content')
    out = note.dumps(contentType=constants.TYPE_TEXT_PLAIN)
    self.assertEqual('content', out)

  #----------------------------------------------------------------------------
  def test_sifn_load(self):
    note = NoteItem.loads('<note><SIFVersion>1.1</SIFVersion><Subject>this note name</Subject><Body>content</Body></note>', contentType=constants.TYPE_SIF_NOTE)
    self.assertEqual('this note name', note.name)
    self.assertEqual('content', note.body)

  #----------------------------------------------------------------------------
  def test_sifn_dump(self):
    note = NoteItem(name='this note name', body='content')
    out = note.dumps(contentType=constants.TYPE_SIF_NOTE, version='1.1')
    self.assertEqual('<note><SIFVersion>1.1</SIFVersion><Subject>this note name</Subject><Body>content</Body></note>', out)

  #----------------------------------------------------------------------------
  def test_sifn_ext_load(self):
    note = NoteItem.loads('<note><SIFVersion>1.1</SIFVersion><Subject>this note name</Subject><Body>content</Body><filename>this-note-name.txt</filename></note>', contentType=constants.TYPE_SIF_NOTE)
    self.assertEqual('this note name', note.name)
    self.assertEqual('content', note.body)
    self.assertEqual(dict(filename=['this-note-name.txt']), note.extensions)

  #----------------------------------------------------------------------------
  def test_sifn_ext_dump(self):
    note = NoteItem(name='this note name', body='content')
    note.addExtension('filename', 'this-note-name.txt')
    out = note.dumps(contentType=constants.TYPE_SIF_NOTE, version='1.1')
    self.assertEqual('<note><SIFVersion>1.1</SIFVersion><Subject>this note name</Subject><Body>content</Body><filename>this-note-name.txt</filename></note>', out)

  #----------------------------------------------------------------------------
  def test_bad_contentType_load(self):
    vcard = '''BEGIN:VCARD
VERSION:3.0
PRODID:-//UnitTest//vCard 3.0//
UID:local:12345
END:VCARD
'''
    self.assertRaises(common.InvalidContentType,
                      NoteItem.loads,
                      vcard, contentType=constants.TYPE_VCARD_V30)

  #----------------------------------------------------------------------------
  def test_bad_contentType_dump(self):
    note = NoteItem(name='this note name', body='content')
    self.assertRaises(common.InvalidContentType,
                      note.dumps,
                      contentType=constants.TYPE_VCARD_V30)

#------------------------------------------------------------------------------
# end of $Id: test_note.py 23 2012-06-03 19:23:36Z griff1n $
#------------------------------------------------------------------------------
