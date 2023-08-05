# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------
# file: $Id: mapping.py 47 2012-08-13 03:04:52Z griff1n $
# lib:  pysyncml.model.mapping
# auth: griffin <griffin@uberdev.org>
# date: 2012/06/24
# copy: (C) CopyLoose 2012 UberDev <hardcore@uberdev.org>, No Rights Reserved.
#------------------------------------------------------------------------------

'''
The ``pysyncml.model.mapping`` provides the model for mapping
client-side object IDs (LUIDs) to server-side object IDs (GUIDs),
stored only on the server-side.
'''

import sys, logging, inspect
import xml.etree.ElementTree as ET
from sqlalchemy import Column, Integer, Boolean, String, Text, ForeignKey
from sqlalchemy.orm import relation, synonym, backref
from sqlalchemy.orm.exc import NoResultFound
from .. import constants, common

log = logging.getLogger(__name__)

#------------------------------------------------------------------------------
def decorateModel(model):

  #----------------------------------------------------------------------------
  class Mapping(model.DatabaseObject):
    store_id          = Column(Integer, ForeignKey('%s_store.id' % (model.prefix,),
                                                   onupdate='CASCADE', ondelete='CASCADE'),
                               nullable=False, index=True)
    # store             = relation('Store', backref=backref('mappings',
    #                                                       cascade='all, delete-orphan',
    #                                                       passive_deletes=True))
    guid              = Column(String(4095), index=True, nullable=True)
    luid              = Column(String(4095), index=True, nullable=True)

  model.Mapping = Mapping

#------------------------------------------------------------------------------
# end of $Id: mapping.py 47 2012-08-13 03:04:52Z griff1n $
#------------------------------------------------------------------------------
