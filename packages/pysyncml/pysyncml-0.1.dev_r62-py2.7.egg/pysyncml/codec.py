# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------
# file: $Id: codec.py 48 2012-08-20 00:31:01Z griff1n $
# lib:  pysyncml.codec
# auth: griffin <griffin@uberdev.org>
# date: 2012/05/20
# copy: (C) CopyLoose 2012 UberDev <hardcore@uberdev.org>, No Rights Reserved.
#------------------------------------------------------------------------------

'''
The ``pysyncml.codec`` is an internal package that abstracts encoding and
decoding routines for the SyncML payload.
'''

import xml.etree.ElementTree as ET
from . import common, constants, state

#------------------------------------------------------------------------------
# shamelessly scrubbed from:
#   http://homework.nwsnet.de/products/45be_remove-namespace-in-an-xml-document-using-elementtree
# and modified to add the namespace to the attributes
def remove_namespace(doc, namespace):
  '''Remove namespace in the passed document in place.'''
  ns = u'{%s}' % namespace
  nsl = len(ns)
  for elem in doc.getiterator():
    if elem.tag.startswith(ns):
      elem.tag = elem.tag[nsl:]
      elem.attrib['oxmlns'] = namespace

# TODO: convert this to stream-oriented...

#------------------------------------------------------------------------------

class Codec(object):
  def encode(self, xtree):
    '''returns a tuple of (contentType, data)'''
    raise NotImplementedError()
  def decode(self, contentType, xmldata):
    '''
    Returns an ElementTree document model of `xmldata`, which has been
    declared to be of `contentType` format/encoding.
    '''
    raise NotImplementedError()
  @staticmethod
  def factory(codec):
    if codec == constants.CODEC_XML:
      return XmlCodec()
    # if codec == constants.CODEC_WBXML:
    #   return WbxmlCodec()
    raise common.UnknownCodec('unknown or unimplemented codec "%s"' % (codec,))
  @staticmethod
  def autoDecode(contentType, data):
    if not contentType.startswith(constants.TYPE_SYNCML + '+'):
      raise common.InvalidContentType('unknown or unimplemented content type "%s"'
                                      % (contentType,))
    ct = contentType[len(constants.TYPE_SYNCML) + 1:].split(';', 1)[0]
    return Codec.factory(ct).decode(contentType, data)

#------------------------------------------------------------------------------
class XmlCodec(Codec):
  name = constants.CODEC_XML
  def encode(self, xtree):
    return (
      '%s+%s; charset=%s' % (constants.TYPE_SYNCML, constants.CODEC_XML, 'UTF-8'),
      ET.tostring(xtree)#, 'UTF-8')
      )
  def decode(self, contentType, xmldata):
    expCT = '%s+%s' % (constants.TYPE_SYNCML, constants.CODEC_XML)
    if not contentType.startswith(expCT):
      raise common.ProtocolError('received unexpected content-type "%s" (expected "%s")' % \
                                 (contentType, expCT))
    return self.removeNamespaces(ET.fromstring(xmldata))
  def removeNamespaces(self, xtree):
    remove_namespace(xtree, constants.NAMESPACE_SYNCML)
    remove_namespace(xtree, str(constants.NAMESPACE_SYNCML).upper())
    remove_namespace(xtree, constants.NAMESPACE_DEVINF)
    remove_namespace(xtree, constants.NAMESPACE_METINF)
    return xtree

# #------------------------------------------------------------------------------
# class WbxmlCodec(Codec):
#   name = constants.CODEC_WBXML
#   def encode(self, adapter, session, request, xtree):
#     request.contentType = '%s+%s' % (constants.TYPE_SYNCML, constants.CODEC_WBXML)
#     request.body = ET.tostring(xtree)

#------------------------------------------------------------------------------
# end of $Id: codec.py 48 2012-08-20 00:31:01Z griff1n $
#------------------------------------------------------------------------------
