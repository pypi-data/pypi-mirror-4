# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------
# file: $Id: test_helpers.py 60 2012-09-16 20:37:30Z griff1n $
# lib:  pysyncml.test_helpers
# auth: griffin <griffin@uberdev.org>
# date: 2012/06/16
# copy: (C) CopyLoose 2012 UberDev <hardcore@uberdev.org>, No Rights Reserved.
#------------------------------------------------------------------------------

import unittest, sys, re, difflib, logging, xml.dom, xml.dom.minidom
from . import constants, common


#------------------------------------------------------------------------------
class LogFormatter(logging.Formatter):
  levelString = {
    logging.DEBUG:       '[  ] DEBUG   ',
    logging.INFO:        '[--] INFO    ',
    logging.WARNING:     '[++] WARNING ',
    logging.ERROR:       '[**] ERROR   ',
    logging.CRITICAL:    '[**] CRITICAL',
    }
  def __init__(self, logsource, *args, **kw):
    logging.Formatter.__init__(self, *args, **kw)
    self.logsource = logsource
  def format(self, record):
    msg = record.getMessage()
    pfx = '%s|%s: ' % (LogFormatter.levelString[record.levelno], record.name) \
          if self.logsource else \
          '%s ' % (LogFormatter.levelString[record.levelno],)
    if msg.find('\n') < 0:
      return '%s%s' % (pfx, record.getMessage())
    return pfx + ('\n' + pfx).join(msg.split('\n'))

#------------------------------------------------------------------------------
def setlogging(enabled):
  if not enabled:
    # kill logging
    logging.disable(logging.CRITICAL)
    return
  rootlog = logging.getLogger()
  handler = logging.StreamHandler(sys.stderr)
  handler.setFormatter(LogFormatter(True))
  rootlog.addHandler(handler)
  rootlog.setLevel(logging.DEBUG)

#------------------------------------------------------------------------------
def makestats(mode=constants.SYNCTYPE_TWO_WAY, conflicts=0, merged=0,
              hereAdd=0, hereMod=0, hereDel=0, hereErr=0,
              peerAdd=0, peerMod=0, peerDel=0, peerErr=0):
  return dict(mode=mode, conflicts=conflicts, merged=merged,
              hereAdd=hereAdd, hereMod=hereMod, hereDel=hereDel, hereErr=hereErr,
              peerAdd=peerAdd, peerMod=peerMod, peerDel=peerDel, peerErr=peerErr)

#------------------------------------------------------------------------------
def stats2str(stats):
  if 'mode' not in stats:
    ret = ''
    for k, v in stats.items():
      if len(ret) > 0:
        ret += ', '
      ret += k + stats2str(v)
    return ret
  ret = [common.mode2string(common.synctype2alert(stats['mode']))]
  for attr in (
    'hereAdd', 'hereMod', 'hereDel', 'hereErr',
    'peerAdd', 'peerMod', 'peerDel', 'peerErr',
    'conflicts', 'merged' ):
    if attr in stats and stats[attr] != 0:
      ret.append('%s=%d' % (attr, stats[attr]))
  return '(' + '; '.join(ret) + ')'

#------------------------------------------------------------------------------
def deepclone(obj):
  if isinstance(obj, basestring):
    return obj
  try:
    ret = dict()
    for k, v in obj.items():
      ret[k] = deepclone(v)
    return ret
  except AttributeError:
    pass
  try:
    return [deepclone(e) for e in obj]
  except TypeError:
    pass
  return obj

#------------------------------------------------------------------------------
def stripsame(dict1, dict2):
  try:
    for key in dict1.keys():
      if key not in dict2:
        continue
      if cmp(dict1.get(key), dict2.get(key)) == 0:
        del dict1[key]
        del dict2[key]
        continue
      stripsame(dict1.get(key), dict2.get(key))
  except AttributeError:
    return

#------------------------------------------------------------------------------
class TrimDictEqual:

  #----------------------------------------------------------------------------
  def assertTrimDictEqual(self, chk, tgt, msg=None):
    try:
      self.assertEqual(chk, tgt, msg)
      return
    except Exception:
      pass
    chkdup = deepclone(chk)
    tgtdup = deepclone(tgt)
    stripsame(chkdup, tgtdup)
    try:
      self.assertEqual(chkdup, tgtdup, msg)
    except Exception:
      raise
    # hm. we somehow stripped the difference... raise the old one...
    self.assertEqual(chk, tgt, msg)

#------------------------------------------------------------------------------
class MultiLineEqual:

  #----------------------------------------------------------------------------
  def assertMultiLineEqual(self, chk, tgt, msg=None):
    try:
      self.assertEqual(chk, tgt, msg)
      return
    except Exception:
      if not isinstance(chk, basestring) \
         or not isinstance(tgt, basestring):
        raise
    print '%s, diff:' % (msg or 'FAIL',)
    print '--- expected'
    print '+++ received'
    differ = difflib.Differ()
    diff = list(differ.compare(chk.split('\n'), tgt.split('\n')))
    cdiff = []
    need = -1
    for idx, line in enumerate(diff):
      if line[0] != ' ':
        need = idx + 2
      if idx > need \
         and line[0] == ' ' \
         and ( len(diff) <= idx + 1 or diff[idx + 1][0] == ' ' ) \
         and ( len(diff) <= idx + 2 or diff[idx + 2][0] == ' ' ):
        continue
      if idx > need:
        cdiff.append('@@ %d @@' % (idx + 1,))
        need = idx + 2
      # if line.startswith('?'):
      #   cdiff.append(line.strip())
      # else:
      #   cdiff.append(line)
      cdiff.append(line.rstrip())
    for line in cdiff:
      print line
    self.assertEqual('expected', 'received')

#------------------------------------------------------------------------------
def removeIgnorableWhitespace(node):
  rem = []
  for n in node.childNodes:
    if n.nodeType == xml.dom.Node.ELEMENT_NODE:
      removeIgnorableWhitespace(n)
    if n.nodeType != xml.dom.Node.TEXT_NODE:
      continue
    if re.match('^\s*$', n.nodeValue):
      rem.append(n)
  for n in rem:
    node.removeChild(n)

#------------------------------------------------------------------------------
def canonicalXml(data):
  try:
    ret = xml.dom.minidom.parseString(data)
    removeIgnorableWhitespace(ret)
    return ret.toxml(encoding='utf-8').encode('utf-8')
  except Exception:
    # most likely, the input was not valid XML...
    return data

#------------------------------------------------------------------------------
class XmlEqual(MultiLineEqual):

  #----------------------------------------------------------------------------
  def assertEqualXml(self, expected, received, msg=None, tryCanonical=True):
    try:
      self.assertEqual(chk, tgt)
      return
    except Exception:
      if tryCanonical:
        return self.assertEqualXml(canonicalXml(expected), canonicalXml(received),
                                   msg, False)
      def n(s):
        return s.replace('><', '>\n<').replace('>$', '>\n$').replace(')<', ')\n<')
      self.maxDiff = None
      self.assertMultiLineEqual(n(str(expected)), n(str(received)), msg)

#------------------------------------------------------------------------------
# end of $Id: test_helpers.py 60 2012-09-16 20:37:30Z griff1n $
#------------------------------------------------------------------------------
