# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------
# file: $Id: test_file.py 44 2012-08-12 15:59:12Z griff1n $
# lib:  pysyncml.items.test_file
# auth: griffin <griffin@uberdev.org>
# date: 2012/05/19
# copy: (C) CopyLoose 2012 UberDev <hardcore@uberdev.org>, No Rights Reserved.
#------------------------------------------------------------------------------

import unittest, logging
from .file import FileItem

# kill logging
logging.disable(logging.CRITICAL)

#------------------------------------------------------------------------------
class TestFile(unittest.TestCase):

  #----------------------------------------------------------------------------
  def test_dump_simple(self):
    fi = FileItem(name='filename.ext', body='some text.\n')
    self.assertEqual(
      ('application/vnd.omads-file+xml', '1.2',
       '<File><name>filename.ext</name><body>some text.\n</body></File>'),
      fi.dumps())

  #----------------------------------------------------------------------------
  def test_load_simple(self):
    fi  = FileItem.loads('<File><name>filename.ext</name><body>some text.\n</body></File>')
    chk = FileItem(name='filename.ext', body='some text.\n')
    self.assertEqual(chk, fi)

  #----------------------------------------------------------------------------
  def test_dump_attributes(self):
    fi = FileItem(name='n', hidden=True, system=False)
    self.assertEqual(
      ('application/vnd.omads-file+xml', '1.2',
       '<File><name>n</name><attributes><h>true</h><s>false</s></attributes></File>'),
      fi.dumps())

  #----------------------------------------------------------------------------
  def test_load_attributes(self):
    fi  = FileItem.loads('<File><name>n</name><attributes><h>true</h><s>false</s></attributes></File>')
    chk = FileItem(name='n', hidden=True, system=False)
    self.assertEqual(chk, fi)

  #----------------------------------------------------------------------------
  def test_dump_dates(self):
    fi = FileItem(id='0', name='n', created=1234567890)
    self.assertEqual(
      ('application/vnd.omads-file+xml', '1.2',
       '<File><name>n</name><created>20090213T233130Z</created></File>'),
      fi.dumps())

  #----------------------------------------------------------------------------
  def test_load_dates(self):
    fi  = FileItem.loads('<File><name>n</name><created>20090213T233130Z</created></File>')
    chk = FileItem(name='n', created=1234567890)
    self.assertEqual(chk, fi)

#------------------------------------------------------------------------------
# end of $Id: test_file.py 44 2012-08-12 15:59:12Z griff1n $
#------------------------------------------------------------------------------
