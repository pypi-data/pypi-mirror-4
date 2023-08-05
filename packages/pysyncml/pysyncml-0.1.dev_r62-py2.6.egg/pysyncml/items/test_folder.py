# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------
# folder: $Id: test_folder.py 44 2012-08-12 15:59:12Z griff1n $
# lib:  pysyncml.items.test_folder
# auth: griffin <griffin@uberdev.org>
# date: 2012/05/19
# copy: (C) CopyLoose 2012 UberDev <hardcore@uberdev.org>, No Rights Reserved.
#------------------------------------------------------------------------------

import unittest, logging
from .folder import FolderItem

# kill logging
logging.disable(logging.CRITICAL)

#------------------------------------------------------------------------------
class TestFolder(unittest.TestCase):

  #----------------------------------------------------------------------------
  def test_dump_simple(self):
    fi = FolderItem(name='foldername')
    self.assertEqual(
      ('application/vnd.omads-folder+xml', '1.2',
       '<Folder><name>foldername</name></Folder>'),
      fi.dumps())

  #----------------------------------------------------------------------------
  def test_load_simple(self):
    fi  = FolderItem.loads('<Folder><name>foldername</name></Folder>')
    chk = FolderItem(name='foldername')
    self.assertEqual(chk, fi)

  #----------------------------------------------------------------------------
  def test_dump_attributes(self):
    fi = FolderItem(name='n', hidden=True, system=False)
    self.assertEqual(
      ('application/vnd.omads-folder+xml', '1.2',
       '<Folder><name>n</name><attributes><h>true</h><s>false</s></attributes></Folder>'),
      fi.dumps())

  #----------------------------------------------------------------------------
  def test_load_attributes(self):
    fi  = FolderItem.loads('<Folder><name>n</name><attributes><h>true</h><s>false</s></attributes></Folder>')
    chk = FolderItem(name='n', hidden=True, system=False)
    self.assertEqual(chk, fi)

  #----------------------------------------------------------------------------
  def test_dump_dates(self):
    fi = FolderItem(name='n', created=1234567890)
    self.assertEqual(
      ('application/vnd.omads-folder+xml', '1.2',
       '<Folder><name>n</name><created>20090213T233130Z</created></Folder>'),
      fi.dumps())

  #----------------------------------------------------------------------------
  def test_load_dates(self):
    fi  = FolderItem.loads('<Folder><name>n</name><created>20090213T233130Z</created></Folder>')
    chk = FolderItem(name='n', created=1234567890)
    self.assertEqual(chk, fi)

#------------------------------------------------------------------------------
# end of $Id: test_folder.py 44 2012-08-12 15:59:12Z griff1n $
#------------------------------------------------------------------------------
