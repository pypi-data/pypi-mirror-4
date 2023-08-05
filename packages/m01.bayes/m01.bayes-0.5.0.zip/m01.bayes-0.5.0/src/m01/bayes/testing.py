###############################################################################
#
# Copyright (c) 2010 Projekt01 GmbH and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
###############################################################################
"""
$Id:$
"""
__docformat__ = "reStructuredText"

import zope.interface
import zope.schema

import m01.mongo.interfaces
import m01.mongo.item
from m01.mongo.fieldproperty import MongoFieldProperty

import m01.bayes.bayes

##############################################################################
#
# test components
#
##############################################################################

# document
class IDocument(m01.mongo.interfaces.IMongoStorageItem):
    """Document based on m01.mongo item"""

    text = zope.schema.Text(
        title=u'Text',
        description=u'Text',
        default=u'',
        required=False)


class Document(m01.mongo.item.MongoStorageItem):
    """Sample document"""

    zope.interface.implements(IDocument)

    dumpNames = ['words']

    text = MongoFieldProperty(IDocument['text'])

    @property
    def words(self):
        return self.text.split()


class TestCollectionMixin(object):
    """Fake test collection mixin class"""

    @property
    def collection(self):
        db = m01.mongo.testing.getTestDatabase()
        return db['collection']

    def getMemoryCollection(self):
        db = m01.mongo.testing.getTestDatabase()
        return db['memory']


class SampleBayesSubItem(TestCollectionMixin, m01.bayes.bayes.BayesSubItem):
    """Sample BayesSubItem."""


class SampleBayesObject(TestCollectionMixin, m01.bayes.bayes.BayesObject):
    """Sample BayesObject."""


class SampleBayesContainerItem(TestCollectionMixin,
    m01.bayes.bayes.BayesContainerItem):
    """Sample BayesContainerItem."""
