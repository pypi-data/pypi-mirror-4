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

import zope.i18nmessageid
import zope.schema

import m01.mongo.interfaces

_ = zope.i18nmessageid.MessageFactory('p01')


class IBayesMemoryContainer(m01.mongo.interfaces.IMongoContainer):
    """BayesMemoryContainer"""


class IBayesMemory(m01.mongo.interfaces.IMongoContainerItem):
    """BayesMemory"""

    data = zope.schema.Dict(
        title=u'Memory data',
        description=u'Memory data',
        key_type=zope.schema.TextLine(),
        value_type=zope.schema.Dict(),
        default={},
        required=False)


class IBayesSchema(zope.interface.Interface):
    """Bayesian classifier base class"""

    useRobinsonFisher = zope.schema.Bool(
        title=u'Robinson Fisher',
        description=u'Robinson Fisher',
        default=True,
        required=True)

    memory = zope.schema.Dict(
        title=u'Memory',
        description=u'Memory',
        default=None,
        required=True)

    pools = zope.schema.Dict(
        title=u'Pools',
        description=u'Pools',
        default=None,
        required=True)

    poolCounters = zope.schema.Dict(
        title=u'Pool Counters',
        description=u'Pool Counters',
        default=None,
        required=True)

    corpus = zope.schema.Dict(
        title=u'Corpus',
        description=u'Corpus',
        default=None,
        required=True)

    corpusCounter = zope.schema.Int(
        title=u'Corpus Counter',
        description=u'Corpus Counter',
        default=0,
        required=True)

    def clear(self):
        """Remove all data"""

    def train(key, poolNameOrNames, tokens):
        """Train Bayes by telling that item belongs in a pool.
        
        Note, this method can also train already trained tokens. Old tokens
        get removed based on the tokens stored in our internal memory.
        """
    def untrain(key, poolNameOrNames=None):
        """Untrain Bayes by telling that item belongs not in a pool anymore.
        
        Note, use this method only if you need to untrain/remove tokens.
        If you need to update an existing key/pool, you can use the train
        method which knows how to remove previous trained tokens.
        """

    def guess(tokens):
        """Computes the probability for a given list of words as a list of
        poolName/probability tuples.
        """

    def getPoolNames():
        """Return a list of pool names"""

    def getPoolTokens(poolName):
        """Return a list of the tokens in this pool"""

    def getPoolData(poolName):
        """Return a list of the (token, count) tuples"""

    def __contains__(key):
        """Returns True/False if a given key is trained."""

    def __len__():
        """Return the pool lenght"""

    def exportMemoryData():
        """Export memory data as json string"""

    def importMemoryData(jsonDataStr):
        """Import bayes data including train if item doesn't exist"""


class IBayesObject(IBayesSchema, m01.mongo.interfaces.IMongoObject):
    """Bayesian classifier object"""


class IBayesSubItem(IBayesSchema, m01.mongo.interfaces.IMongoSubItem):
    """Bayesian classifier base class"""


class IBayesContainerItem(IBayesSchema,
    m01.mongo.interfaces.IMongoContainerItem):
    """Bayesian classifier base class"""
