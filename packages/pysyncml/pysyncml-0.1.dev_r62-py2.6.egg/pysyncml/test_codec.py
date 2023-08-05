# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------
# file: $Id: test_common.py 38 2012-07-21 17:38:23Z griff1n $
# lib:  pysyncml.test_common
# auth: griffin <griffin@uberdev.org>
# date: 2012/05/30
# copy: (C) CopyLoose 2012 UberDev <hardcore@uberdev.org>, No Rights Reserved.
#------------------------------------------------------------------------------

import unittest, re
import xml.etree.ElementTree as ET
from . import codec, constants, test_helpers

#------------------------------------------------------------------------------
class TestCodec(unittest.TestCase, test_helpers.MultiLineEqual):

  #----------------------------------------------------------------------------
  def test_encode_utf8(self):
    uni = u'\u30c6\u30b9\u30c8'
    raw = 'テスト'
    self.assertEqual(uni, raw.decode('utf-8'))
    xdoc = ET.Element('root')
    xdoc.text = uni
    contentType, data = codec.Codec.factory(constants.CODEC_XML).encode(xdoc)
    self.assertEqual('application/vnd.syncml+xml; charset=UTF-8', contentType)
    # TODO: determine which output i actually want...
    self.assertEqual('<root>&#12486;&#12473;&#12488;</root>', data)
    #self.assertEqual('<?xml version=\'1.0\' encoding=\'UTF-8\'?>\n<root>\xe3\x83\x86\xe3\x82\xb9\xe3\x83\x88</root>', data)

#------------------------------------------------------------------------------
# end of $Id: test_common.py 38 2012-07-21 17:38:23Z griff1n $
#------------------------------------------------------------------------------
