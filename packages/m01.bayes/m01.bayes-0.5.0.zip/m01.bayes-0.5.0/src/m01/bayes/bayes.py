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
"""Bayesian classifier

"""

import operator
import re
import math
import thread
try:
    # python < 2.6 or people using simplejson
    import simplejson as json
except ImportError:
    # python >= 2.6
    import json

import zope.interface

import m01.mongo.item
import m01.mongo.container
import m01.mongo.util
from m01.mongo.fieldproperty import MongoFieldProperty

from m01.bayes import interfaces

def poolNameToKey(poolName):
    """Convert poolName to valid mongodb key"""
    if isinstance(poolName, int):
        poolName = '%s:int' % poolName
    elif isinstance(poolName, bool):
        if poolName:
            poolName = 'true:bool'
        else:
            poolName = 'false:bool'
    return poolName


def keyToPoolName(poolName):
    """Convert mongodb key to poolName"""
    if poolName.endswith(':int'):
        poolName = int(poolName[:-4])
    elif poolName.endswith(':bool'):
        poolName = poolName[:-5]
        if poolName == 'true':
            poolName = True
        elif poolName == 'false':
            poolName = False
    return poolName


def chi2P(chi, df):
    """Return P(chisq >= chi, with df degree of freedom)

    df must be even
    """
    assert df & 1 == 0
    m = chi / 2.0
    sum = term = math.exp(-m)
    for i in range(1, df/2):
        term *= m/i
        sum += term
    return min(sum, 1.0)

class BayesMemory(m01.mongo.base.MongoItemBase):
    """BayesMemory"""

    zope.interface.implements(interfaces.IBayesMemory)

    data = MongoFieldProperty(interfaces.IBayesMemory['data'])

    dumpNames = ['data']

    def __init__(self, data):
        self.data = {}
        super(BayesMemory, self).__init__(data)

    def get(self, key):
        return self.data.get(key)

    def __setitem__(self, key, obj):
        key = unicode(key)
        self.data[key] = obj

    def __delitem__(self, key):
        del self.data[key]

    def __len__(self):
        return len(self.data)

    def keys(self):
        return self.data.keys()


class BayesMemoryContainer(m01.mongo.container.MongoContainer):
    """Memory using external stored items for scaling"""

    zope.interface.implements(interfaces.IBayesMemoryContainer)

    __name__ = u'memory'

    def __init__(self, data):
        self.__parent__ = data['__parent__']

    @property
    def _mpid(self):
        # must return a unique id or BayesMemoryContainer will share it's
        # BayesMemory items
        return self.__parent__._id

    @property
    def collection(self):
        """Returns a thread local shared collection for scheduler items."""
        return self.__parent__.getMemoryCollection()

    @property
    def cacheKey(self):
        return 'bayes.memory.%s.%i' % (id(self), thread.get_ident())

    def load(self, data):
        """Load data into the relevant item type"""
        return BayesMemory(data)

    def __repr__(self):
        return '<%s for %r>' % (self.__class__.__name__,
            self.__parent__.__name__)


class BayesBase(object):
    """Bayesian classifier base class with built-in tokens memory."""

    useRobinsonFisher = MongoFieldProperty(
        interfaces.IBayesSchema['useRobinsonFisher'])
    memory = MongoFieldProperty(interfaces.IBayesSchema['memory'])
    pools = MongoFieldProperty(interfaces.IBayesSchema['pools'])
    poolCounters = MongoFieldProperty(interfaces.IBayesSchema['poolCounters'])
    corpus = MongoFieldProperty(interfaces.IBayesSchema['corpus'])
    corpusCounter = MongoFieldProperty(interfaces.IBayesSchema['corpusCounter'])

    _memory = None

    skipNames = ['memory']
    dumpNames = ['useRobinsonFisher', 'pools', 'poolCounters', 'corpus',
                 'corpusCounter']

    def __init__(self, data):
        # first setup empty defaults
        self.pools = {}
        self.poolCounters = {}
        self.corpus = {}
        self.corpusCounter = 0
        # setup internals (not stored in mongo)
        self.cache = {}
        self._dirty = True
        # now update with given data
        super(BayesBase, self).__init__(data)

    @apply
    def dirty():
        def fget(self):
            return self._dirty
        def fset(self, value):
            self._dirty = value
            self._m_changed = True
        return property(fget, fset)

    def clear(self):
        """Remove all data"""
        self.pools = {}
        self.poolCounters = {}
        self.corpus = {}
        self.corpusCounter = 0
        # setup internals (not stored in mongo)
        self.cache = {}
        self._dirty = True

    def getMemoryCollection(self):
        raise NotImplementedError("Subclass must implement getMemoryCollection")

    @property
    def memory(self):
        if self._memory is None:
            # create and locate BayesMemory container
            self._memory = BayesMemoryContainer({'__parent__': self})
        return self._memory

    def createBayesMemory(self):
        return BayesMemory({'__parent__': self.memory})

    def exportMemoryData(self):
        """Export memory data as json string"""
        data = {}
        for mKey, memory in self.memory.items():
            data[mKey] = memory.data
        return json.dumps(data, sort_keys=True)

    def importMemoryData(self, jsonDataStr):
        """Import bayes data including train if item doesn't exist"""
        data = json.loads(jsonDataStr)
        trained = 0
        ignored = 0
        for mKey, memoryData in data.items():
            for poolName, tokenData in memoryData.items():
                tokens = self._getTokens(tokenData)
                if self.train(mKey, poolName, tokens):
                    trained += 1
                else:
                    ignored += 1
        return trained, ignored

    def update(self):
        """Merges and computes probabilities.
        
        This method get called if guess get called and the dirty flag is set to
        True. The dirty flag get set if we train or untrain items.
        """
        self.cache = {}
        for poolName, pool in self.pools.items():
            poolCounter = self.poolCounters.get(poolName, 0)
            diffCounter = max(self.corpusCounter - poolCounter, 1)
            wordDict = self.cache.setdefault(poolName, {})

            for word, totCounter in self.corpus.items():
                # for every word in the corpus
                # check to see if this pool contains this word
                thisCounter = float(pool.get(word, 0.0))
                if (thisCounter == 0.0):
                	continue
                otherCounter = float(totCounter) - thisCounter

                if not poolCounter:
                    goodMetric = 1.0
                else:
                    goodMetric = min(1.0, otherCounter/poolCounter)
                badMetric = min(1.0, thisCounter/diffCounter)
                f = badMetric / (goodMetric + badMetric)

                # probability thershold
                if abs(f-0.5) >= 0.1 :
                    # GOOD_PROB, BAD_PROB
                    wordDict[word] = max(0.0001, min(0.9999, f))

        # mark as clean
        self.dirty = False

    def getProbs(self, words, wordDict):
        """Extracts the probabilities of tokens in a list of words"""
        probs = [wordDict[word] for word in words if word in wordDict]
        probs.sort(lambda x,y: cmp(y,x))
        return probs[:2048]

    # token memory
    def createTokenData(self, tokens):
        """Setup token/counter dictionary"""
        d = {}
        for token in tokens:
            d.setdefault(token, 0)
            d[token] +=1
        return d

    def _getTokens(self, tokenData):
        """Returns a list of (duplicated) tokens from token memory"""
        res = []
        append = res.append
        for token, counter in tokenData.items():
            while counter:
                counter -= 1
                # do not yield data or we will lose them later
                append(token)
        return res

    def getTrainedTokens(self, itemMemory, poolName):
        tokenData = itemMemory.get(poolName)
        if tokenData is not None:
            return self._getTokens(tokenData)
        else:
            # return an empty list
            return []

    def train(self, key, poolNameOrNames, tokens):
        """Train Bayes by telling that item belongs in a pool.
        
        Note, this method does untrain already trained tokens. Old tokens
        get removed based on the tokens stored in our internal bayes memory.
        """
        if isinstance(poolNameOrNames, basestring):
            poolNames = [poolNameOrNames]
        elif isinstance(poolNameOrNames, m01.mongo.util.MongoListData):
            poolNames = poolNameOrNames.data
        elif isinstance(poolNameOrNames, (tuple, list)):
            # could be a list, tuple
            poolNames = poolNameOrNames
        else:
            # could be a poolName marker (TRUE/FALSE)
            poolNames = [poolNameOrNames]
        try:
            itemMemory = self.memory[key]
        except KeyError, e:
            self.memory[key] = self.createBayesMemory()
            itemMemory = self.memory[key]
        status = False
        for poolName in poolNames:
            poolName = poolNameToKey(poolName)
            trainedTokens = self.getTrainedTokens(itemMemory, poolName)
            if trainedTokens:
                # untrain tokens
                if set(tokens) == set(trainedTokens):
                    # already trained tokens for this pool, skip
                    continue
                self._untrainTokens(poolName, trainedTokens)
                # remove token data, we will add it later if tokens given
                del itemMemory[poolName]
            if tokens:
                # train new tokens
                self._trainTokens(poolName, tokens)
                # set token data
                itemMemory[poolName] = self.createTokenData(tokens)
            self.dirty = True
            status = True
        return status

    def untrain(self, key, poolNameOrNames=None):
        """Untrain Bayes by telling that item belongs not in a pool anymore.
        
        Note, use this method only if you need to untrain/remove tokens.
        If you need to update an existing key/pool, you can use the train
        method which knows how to remove previous trained tokens.
        """
        status = False
        itemMemory = self.memory.get(key)
        if itemMemory is not None:
            if poolNameOrNames is None:
                # get poolNames from our memory
                poolNames = list(itemMemory.keys())
            elif isinstance(poolNameOrNames, basestring):
                poolNames = [poolNameOrNames]
            elif isinstance(poolNameOrNames, m01.mongo.util.MongoListData):
                poolNames = poolNameOrNames.data
            elif isinstance(poolNameOrNames, (tuple, list)):
                # could be a list, tuple
                poolNames = poolNameOrNames
            else:
                # could be a poolName marker (TRUE/FALSE)
                poolNames = [poolNameOrNames]
            # convert bool poolNameOrNames
            for poolName in poolNames:
                poolName = poolNameToKey(poolName)
                trainedTokens = self.getTrainedTokens(itemMemory, poolName)
                if trainedTokens:
                    # untrain tokens
                    self._untrainTokens(poolName, trainedTokens)
                    status = True
                    # remove token data
                    del itemMemory[poolName]
                    if len(itemMemory) == 0:
                        # remove empty itemMemory and provide correct len
                        del self.memory[key]
                    self.dirty = True
        return status

    def _trainTokens(self, poolName, tokens):
        """Train tokens based on token list with duplicated words"""
        pool = self.pools.setdefault(poolName, {})
        wc = 0
        for token in tokens:
            count = pool.get(token, 0)
            pool[token] = count + 1
            count = self.corpus.get(token, 0)
            self.corpus[token] = count + 1
            wc += 1
        c = self.poolCounters.get(poolName, 0)
        c += wc
        self.poolCounters[poolName] = c
        self.corpusCounter += wc

    def _untrainTokens(self, poolName, tokens):
        """Untrain tokens based on token list with duplicated words"""
        pool = self.pools.get(poolName, {})
        pCounter = self.poolCounters.get(poolName, 0)
        for token in tokens:
            count = pool.get(token, 0)
            if count:
                if count == 1:
                    del pool[token]
                else:
                    pool[token] = count - 1
                pCounter -= 1
            count = self.corpus.get(token, 0)
            if count:
                if count == 1:
                    del self.corpus[token]
                else:
                    self.corpus[token] = count - 1
                self.corpusCounter -= 1
        # set counter
        self.poolCounters[poolName] = pCounter

    def guess(self, tokens):
        """Computes the probability for a given list of words as a list of
        poolName/probability tuples.
        """
        tokens = set(tokens)
        if self.dirty:
            self.update()
        res = {}
        if self.useRobinsonFisher:
            combiner = self.robinsonFisher
        else:
            combiner = self.robinson
        for poolNameOrMarker, wordDict in self.cache.items():
            p = self.getProbs(tokens, wordDict)
            if len(p) != 0:
                poolName = keyToPoolName(poolNameOrMarker)
                res[poolName] = combiner(p)
        # convert to a sortable list of poolName/probability factor tuples
        res = res.items()
        res.sort(lambda x,y: cmp(y[1], x[1]))
        return res

    def robinson(self, probs):
        """Computes the probability (Robinson's method)

        P = 1 - prod(1-p)^(1/n)
        Q = 1 - prod(p)^(1/n)
        S = (1 + (P-Q)/(P+Q)) / 2

        """
        nth = 1.0/len(probs)
        P = 1.0 - reduce(operator.mul, map(lambda p: 1.0-p, probs), 1.0) ** nth
        Q = 1.0 - reduce(operator.mul, probs) ** nth
        S = (P - Q) / (P + Q)
        return (1 + S) / 2

    def robinsonFisher(self, probs):
        """Computes the probability (Robinson-Fisher method)

        H = C-1( -2.ln(prod(p)), 2*n )
        S = C-1( -2.ln(prod(1-p)), 2*n )
        I = (1 + H - S) / 2

        """
        n = len(probs)
        try:
            #H = chi2P(-2.0 * math.log(reduce(operator.mul, map(lambda p: p[1], probs), 1.0)), 2*n)
            reduced = reduce(operator.mul, probs, 1.0)
            H = chi2P(-2.0 * math.log(reduced), 2*n)
        except (ValueError, OverflowError), e:
            # math.log can run into a ValueError if reduced is 0.0
            H = 0.0
        try:
            #S = chi2P(-2.0 * math.log(reduce(operator.mul, map(lambda p: 1.0-p[1], probs), 1.0)), 2*n)
            reduced = reduce(operator.mul, map(lambda p: 1.0-p, probs), 1.0)
            S = chi2P(-2.0 * math.log(reduced), 2*n)
        except (ValueError, OverflowError), e:
            # reduce can run into a ValueError if reduced is 0.0
            S = 0.0
        return (1 + H - S) / 2

    # some additional methods
    def getPoolNames(self):
        """Return a list of pool names"""
        return [keyToPoolName(poolName) for poolName in self.pools.keys()]

    def getPoolTokens(self, poolName):
        """Return a list of the tokens in this pool"""
        poolName = poolNameToKey(poolName)
        return self.pools[poolName].keys()

    def getPoolData(self, poolName):
        """Return a list of the (token, count) tuples"""
        poolName = poolNameToKey(poolName)
        return self.pools[poolName].items()

    def __contains__(self, key):
        return key in self.memory

    def __len__(self):
        return len(self.memory)

    def __repr__(self):
        combiner = 'Robinson'
        if self.useRobinsonFisher:
            combiner = 'Robinson-Fisher'
        return '<%s using %s>' % (self.__class__.__name__, combiner)


class BayesSubItem(BayesBase, m01.mongo.item.MongoSubItem):
    """Bayesian classifier sub item implementation."""

    zope.interface.implements(interfaces.IBayesSubItem)


class BayesObject(BayesBase, m01.mongo.item.MongoObject):
    """Bayesian classifier Object implementation."""

    zope.interface.implements(interfaces.IBayesObject)


class BayesContainerItem(BayesBase, m01.mongo.item.MongoContainerItem):
    """Bayesian classifier container item implementation."""

    zope.interface.implements(interfaces.IBayesContainerItem)
