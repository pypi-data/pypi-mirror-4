# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------
# file: $Id: test_common.py 60 2012-09-16 20:37:30Z griff1n $
# lib:  pysyncml.test_common
# auth: griffin <griffin@uberdev.org>
# date: 2012/05/30
# copy: (C) CopyLoose 2012 UberDev <hardcore@uberdev.org>, No Rights Reserved.
#------------------------------------------------------------------------------

import unittest, re
from StringIO import StringIO as sio
from . import common, constants, test_helpers
from .common import adict

#------------------------------------------------------------------------------
class TestCommon(unittest.TestCase, test_helpers.MultiLineEqual):

  maxDiff = None

  #----------------------------------------------------------------------------
  def test_fullClassname(self):
    self.assertEqual('pysyncml.test_common.TestCommon',
                     common.fullClassname(self))

  #----------------------------------------------------------------------------
  def test_indent(self):
    buf = sio()
    out = common.IndentStream(buf, '>>')
    out.write('hi')
    self.assertMultiLineEqual('>>hi', buf.getvalue())
    out.write(', there!')
    out.write('\nhow are you?\n')
    self.assertMultiLineEqual('>>hi, there!\n>>how are you?\n', buf.getvalue())

  #----------------------------------------------------------------------------
  def test_indent_print(self):
    buf = sio()
    out = common.IndentStream(buf, '>>')
    out.write('hi')
    self.assertMultiLineEqual('>>hi', buf.getvalue())
    print >>out, ', there!'
    print >>out, 'how are you?'
    self.assertMultiLineEqual('>>hi, there!\n>>how are you?\n', buf.getvalue())

  #----------------------------------------------------------------------------
  def test_version(self):
    # ensure that the version is always "MAJOR.MINOR.SOMETHING"
    self.assertTrue(re.match(r'^[0-9]+\.[0-9]+\.[0-9a-z.-]*$', common.versionString)
                    is not None)

  #----------------------------------------------------------------------------
  def test_describeStats(self):
    buf = sio()
    stats = dict(note=adict(
      mode=constants.SYNCTYPE_TWO_WAY,conflicts=0,merged=0,
      hereAdd=10,hereMod=0,hereDel=0,hereErr=0,
      peerAdd=0,peerMod=0,peerDel=2,peerErr=0))
    common.describeStats(stats, buf)
    chk = '''
+--------+------+-----------------------+-----------------------+-----------+
|        |      |         Local         |        Remote         | Conflicts |
| Source | Mode | Add | Mod | Del | Err | Add | Mod | Del | Err | Col | Mrg |
+--------+------+-----+-----+-----+-----+-----+-----+-----+-----+-----+-----+
|   note |  <>  |  10 |  -  |  -  |  -  |  -  |  -  |   2 |  -  |  -  |  -  |
+--------+------+-----+-----+-----+-----+-----+-----+-----+-----+-----+-----+
|                  10 local changes and 2 remote changes.                   |
+---------------------------------------------------------------------------+
'''.lstrip()
    self.assertMultiLineEqual(chk, buf.getvalue())

  #----------------------------------------------------------------------------
  def test_describeStats_noTotals(self):
    buf = sio()
    stats = dict(note=adict(
      mode=constants.SYNCTYPE_TWO_WAY,conflicts=0,merged=0,
      hereAdd=10,hereMod=0,hereDel=0,hereErr=0,
      peerAdd=0,peerMod=0,peerDel=2,peerErr=0))
    common.describeStats(stats, buf, totals=False)
    chk = '''
+--------+------+-----------------------+-----------------------+-----------+
|        |      |         Local         |        Remote         | Conflicts |
| Source | Mode | Add | Mod | Del | Err | Add | Mod | Del | Err | Col | Mrg |
+--------+------+-----+-----+-----+-----+-----+-----+-----+-----+-----+-----+
|   note |  <>  |  10 |  -  |  -  |  -  |  -  |  -  |   2 |  -  |  -  |  -  |
+--------+------+-----+-----+-----+-----+-----+-----+-----+-----+-----+-----+
'''.lstrip()
    self.assertMultiLineEqual(chk, buf.getvalue())

  #----------------------------------------------------------------------------
  def test_describeStats_title(self):
    buf = sio()
    stats = dict(note=adict(
      mode=constants.SYNCTYPE_TWO_WAY,conflicts=0,merged=0,
      hereAdd=10,hereMod=0,hereDel=0,hereErr=0,
      peerAdd=0,peerMod=0,peerDel=2,peerErr=0))
    common.describeStats(stats, buf, title='Synchronization Summary')
    chk = '''
+---------------------------------------------------------------------------+
|                          Synchronization Summary                          |
+--------+------+-----------------------+-----------------------+-----------+
|        |      |         Local         |        Remote         | Conflicts |
| Source | Mode | Add | Mod | Del | Err | Add | Mod | Del | Err | Col | Mrg |
+--------+------+-----+-----+-----+-----+-----+-----+-----+-----+-----+-----+
|   note |  <>  |  10 |  -  |  -  |  -  |  -  |  -  |   2 |  -  |  -  |  -  |
+--------+------+-----+-----+-----+-----+-----+-----+-----+-----+-----+-----+
|                  10 local changes and 2 remote changes.                   |
+---------------------------------------------------------------------------+
'''.lstrip()
    self.assertMultiLineEqual(chk, buf.getvalue())

  #----------------------------------------------------------------------------
  def test_describeStats_errors(self):
    buf = sio()
    stats = dict(note=adict(
      mode=constants.SYNCTYPE_TWO_WAY,conflicts=0,merged=0,
      hereAdd=10,hereMod=0,hereDel=0,hereErr=1,
      peerAdd=0,peerMod=0,peerDel=1,peerErr=2))
    common.describeStats(stats, buf, title='Synchronization Summary')
    chk = '''
+---------------------------------------------------------------------------+
|                          Synchronization Summary                          |
+--------+------+-----------------------+-----------------------+-----------+
|        |      |         Local         |        Remote         | Conflicts |
| Source | Mode | Add | Mod | Del | Err | Add | Mod | Del | Err | Col | Mrg |
+--------+------+-----+-----+-----+-----+-----+-----+-----+-----+-----+-----+
|   note |  <>  |  10 |  -  |  -  |   1 |  -  |  -  |   1 |   2 |  -  |  -  |
+--------+------+-----+-----+-----+-----+-----+-----+-----+-----+-----+-----+
|              10 local changes, 1 remote change and 3 errors.              |
+---------------------------------------------------------------------------+
'''.lstrip()
    self.assertMultiLineEqual(chk, buf.getvalue())

  #----------------------------------------------------------------------------
  def test_describeStats_multiwide(self):
    buf = sio()
    stats = dict(note=adict(
      mode=constants.SYNCTYPE_SLOW_SYNC,conflicts=0,merged=0,
      hereAdd=1308,hereMod=0,hereDel=2,hereErr=0,
      peerAdd=0,peerMod=0,peerDel=0,peerErr=0),
                 contacts=adict(
      mode=constants.SYNCTYPE_REFRESH_FROM_SERVER,conflicts=0,merged=0,
      hereAdd=0,hereMod=0,hereDel=0,hereErr=0,
      peerAdd=10387,peerMod=0,peerDel=0,peerErr=0))
    common.describeStats(stats, buf)
    chk = '''
+----------+------+-------------------------+--------------------------+-----------+
|          |      |          Local          |          Remote          | Conflicts |
|   Source | Mode |  Add  | Mod | Del | Err |  Add   | Mod | Del | Err | Col | Mrg |
+----------+------+-------+-----+-----+-----+--------+-----+-----+-----+-----+-----+
| contacts |  <=  |   -   |  -  |  -  |  -  | 10,387 |  -  |  -  |  -  |  -  |  -  |
|     note |  SS  | 1,308 |  -  |   2 |  -  |   -    |  -  |  -  |  -  |  -  |  -  |
+----------+------+-------+-----+-----+-----+--------+-----+-----+-----+-----+-----+
|                  1,310 local changes and 10,387 remote changes.                  |
+----------------------------------------------------------------------------------+
'''.lstrip()
    self.assertMultiLineEqual(chk, buf.getvalue())

  #----------------------------------------------------------------------------
  def test_describeStats_titleAndTotals(self):
    buf = sio()
    stats = dict(note=adict(
      mode=constants.SYNCTYPE_SLOW_SYNC,conflicts=0,merged=0,
      hereAdd=1308,hereMod=0,hereDel=2,hereErr=0,
      peerAdd=0,peerMod=0,peerDel=0,peerErr=0),
                 contacts=adict(
      mode=constants.SYNCTYPE_REFRESH_FROM_SERVER,conflicts=0,merged=0,
      hereAdd=0,hereMod=0,hereDel=0,hereErr=0,
      peerAdd=10387,peerMod=0,peerDel=0,peerErr=0))
    common.describeStats(stats, buf, title='Synchronization Summary', details=False)
    chk = '''
+------------------------------------------------+
|            Synchronization Summary             |
| 1,310 local changes and 10,387 remote changes. |
+------------------------------------------------+
'''.lstrip()
    self.assertMultiLineEqual(chk, buf.getvalue())

  #----------------------------------------------------------------------------
  def test_describeStats_totals(self):
    buf = sio()
    stats = dict(note=adict(
      mode=constants.SYNCTYPE_SLOW_SYNC,conflicts=0,merged=0,
      hereAdd=1308,hereMod=0,hereDel=2,hereErr=0,
      peerAdd=0,peerMod=0,peerDel=0,peerErr=0),
                 contacts=adict(
      mode=constants.SYNCTYPE_REFRESH_FROM_SERVER,conflicts=0,merged=0,
      hereAdd=0,hereMod=0,hereDel=0,hereErr=0,
      peerAdd=10387,peerMod=0,peerDel=0,peerErr=0))
    common.describeStats(stats, buf, details=False)
    chk = '''
+------------------------------------------------+
| 1,310 local changes and 10,387 remote changes. |
+------------------------------------------------+
'''.lstrip()
    self.assertMultiLineEqual(chk, buf.getvalue())
    stats['note'].merged    = 3
    stats['note'].conflicts = 2
    stats['note'].hereErr   = 2
    buf = sio()
    common.describeStats(stats, buf, details=False)
    chk = '''
+------------------------------------------------------------------------------------+
| 1,310 local changes, 10,387 remote changes and 2 errors: 3 merges and 2 conflicts. |
+------------------------------------------------------------------------------------+
'''.lstrip()
    self.assertMultiLineEqual(chk, buf.getvalue())

#------------------------------------------------------------------------------
# end of $Id: test_common.py 60 2012-09-16 20:37:30Z griff1n $
#------------------------------------------------------------------------------
