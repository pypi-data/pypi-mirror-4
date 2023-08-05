======
README
======

This package provides a bayesian classifier which stores its data in mongodb
useing the m01.mongo package.


  >>> import m01.mongo
  >>> from pprint import pprint
  >>> def printMemory(memory):
  ...     data = {}
  ...     for k, v in memory.items():
  ...         data[k] = v.dump()
  ...     data = m01.mongo.dictify(data)
  ...     pprint(data)

  >>> def printBayes(bayes):
  ...     data = bayes.dump()
  ...     data['memory'] = {}
  ...     for k, v in bayes.memory.items():
  ...         data['memory'][k] = v.dump()
  ...     data = m01.mongo.dictify(data)
  ...     pprint(data)

Condition
---------

Befor we start testing, check if our thread local cache is empty or if we have
let over some junk from previous tests:

  >>> from m01.mongo import LOCAL
  >>> pprint(LOCAL.__dict__)
  {}


Setup
-----

First import some components:

  >>> from pprint import pprint
  >>> import transaction

  >>> import m01.mongo
  >>> import m01.bayes.bayes
  >>> import m01.bayes.testing

We also need a container which we can use for store out Bayes container item.

  >>> class MongoContainer(m01.mongo.container.MongoContainer):
  ...     """Mongo container"""
  ... 
  ...     _id = m01.mongo.getObjectId(0)
  ... 
  ...     def __init__(self):
  ...         pass
  ... 
  ...     @property
  ...     def collection(self):
  ...         return m01.mongo.testing.getRootItems()
  ...
  ...     @property
  ...     def cacheKey(self):
  ...         return 'root'
  ... 
  ...     def load(self, data):
  ...         """Load data into the right mongo item."""
  ...         return m01.bayes.testing.SampleBayesContainerItem(data)
  ... 
  ...     def __repr__(self):
  ...         return '<%s %s>' % (self.__class__.__name__, self._id)



As you can see our MongoContainer class defines a static mongo ObjectID as _id.
This means the same _id get use every time. This _id acts as our __parent__
reference but that's another part, see m01.mongo/container.txt for more info

  >>> def getContainer():
  ...     return MongoContainer()

Here is our bayes container item:

  >>> container = getContainer()
  >>> container
  <MongoContainer 000000000000000000000000>


Bayes
-----

Now we are able to setup our Bayes classifier item:

  >>> bayes = m01.bayes.testing.SampleBayesContainerItem({})

and add it to our mongo container:

  >>> container[u'bayes'] = bayes
  >>> bayes
  <SampleBayesContainerItem using Robinson-Fisher>

  >>> bayes.__name__
  u'bayes'

  >>> bayes._id
  ObjectId('...')


Now setup a sample document:

  >>> _id = m01.mongo.getObjectId(1)
  >>> data = {'_id': _id, 'text': u'This dummy doc contains dummy text'}
  >>> doc = m01.bayes.testing.Document(data)
  >>> doc.__name__
  u'000000010000000000000000'


untrain
-------

Now let's train our document:

  >>> bayes.train(doc.__name__, 'words', doc.words)
  True

if we again train the doc with the same values, we will get False as return
value:

  >>> bayes.train(doc.__name__, 'words', doc.words)
  False

As you can see we have trained 1 document. This document is referenced by it's
mongo ObjectId in the memory dict:

  >>> printMemory(bayes.memory)
  {u'000000010000000000000000': {'__name__': u'000000010000000000000000',
                                 '_id': ObjectId('...'),
                                 '_pid': ObjectId('...'),
                                 '_type': u'BayesMemory',
                                 '_version': 0,
                                 'created': datetime.datetime(...),
                                 'data': {u'words': {u'This': 1,
                                                     u'contains': 1,
                                                     u'doc': 1,
                                                     u'dummy': 2,
                                                     u'text': 1}}}}

and our corpus contains all words as key and the amount of how many times they
are used in the given text:

  >>> bayes.corpus
  {u'This': 1, u'dummy': 2, u'contains': 1, u'text': 1, u'doc': 1}

and we also got a new pool called words which contains all the words in it
inclding counters for each word:

  >>> bayes.pools
  {'words': {u'This': 1, u'dummy': 2, u'contains': 1, u'text': 1, u'doc': 1}}

Now let's store the bayes item and write the data back to the mongodb:

  >>> pprint(LOCAL.__dict__)
  {'MongoTransactionDataManager': <m01.mongo.tm.MongoTransactionDataManager object at ...>,
   'bayes.memory...': {'added': {u'000000010000000000000000': <BayesMemory u'000000010000000000000000'>},
                                  'loaded': {u'000000010000000000000000': <BayesMemory u'000000010000000000000000'>},
                                  'removed': {}},
   'root': {'added': {u'bayes': <SampleBayesContainerItem using Robinson-Fisher>},
            'loaded': {u'bayes': <SampleBayesContainerItem using Robinson-Fisher>},
            'removed': {}}}

  >>> transaction.commit()

  >>> pprint(LOCAL.__dict__)
  {}

Ok, that's it, check if we can get our bayes item back from the mongodb:

  >>> root = getContainer()
  >>> root['bayes']
  <SampleBayesContainerItem using Robinson-Fisher>

And if we loaded the bayes data correct:

  >>> printMemory(bayes.memory)
  {u'000000010000000000000000': {'__name__': u'000000010000000000000000',
                                 '_id': ObjectId('...'),
                                 '_pid': ObjectId('...'),
                                 '_type': u'BayesMemory',
                                 '_version': 1,
                                 'created': datetime.datetime(...),
                                 'data': {u'words': {u'This': 1,
                                                     u'contains': 1,
                                                     u'doc': 1,
                                                     u'dummy': 2,
                                                     u'text': 1}},
                                 'modified': datetime.datetime(...)}}

  >>> bayes.corpus
  {u'This': 1, u'dummy': 2, u'contains': 1, u'text': 1, u'doc': 1}

  >>> bayes.pools
  {'words': {u'This': 1, u'dummy': 2, u'contains': 1, u'text': 1, u'doc': 1}}

Yeah, it seems that your bayes item can dump and load our data.


As next we will add more documents and check the bayesian classifiers:

  >>> _id2 = m01.mongo.getObjectId(2)
  >>> data2 = {'_id': _id2, 'text': u'This is more dummy text'}
  >>> doc2 = m01.bayes.testing.Document(data2)
  >>> doc2.__name__
  u'000000020000000000000000'

Now let's train the second document:

  >>> bayes.train(doc2.__name__, 'words', doc2.words)
  True

and check the bayes internals:

  >>> printMemory(bayes.memory)
  {u'000000010000000000000000': {'__name__': u'000000010000000000000000',
                                 '_id': ObjectId('...'),
                                 '_pid': ObjectId('...'),
                                 '_type': u'BayesMemory',
                                 '_version': 1,
                                 'created': datetime.datetime(...),
                                 'data': {u'words': {u'This': 1,
                                                     u'contains': 1,
                                                     u'doc': 1,
                                                     u'dummy': 2,
                                                     u'text': 1}},
                                 'modified': datetime.datetime(...)},
   u'000000020000000000000000': {'__name__': u'000000020000000000000000',
                                 '_id': ObjectId('...'),
                                 '_pid': ObjectId('...'),
                                 '_type': u'BayesMemory',
                                 '_version': 0,
                                 'created': datetime.datetime(...),
                                 'data': {u'words': {u'This': 1,
                                                     u'dummy': 1,
                                                     u'is': 1,
                                                     u'more': 1,
                                                     u'text': 1}}}}

and our corpus contains all words as key and the amount of how many times they
are used in the given text:

  >>> pprint(bayes.corpus)
  {u'This': 2,
   u'contains': 1,
   u'doc': 1,
   u'dummy': 3,
   u'is': 1,
   u'more': 1,
   u'text': 2}

and we also got a new pool called words which contains all the words in it
inclding counters for each word:

  >>> pprint(bayes.pools)
  {'words': {u'This': 2,
             u'contains': 1,
             u'doc': 1,
             u'dummy': 3,
             u'is': 1,
             u'more': 1,
             u'text': 2}}

commit:

  >>> transaction.commit()

and start guessing:

  >>> transaction.commit()
  >>> guess = bayes.guess(['This', 'dummy'])
  >>> guess
  [('words', 0.999...)]

  >>> guess2 = bayes.guess(['This', 'nada'])
  >>> guess2
  [('words', 0.999...)]

  >>> guess3 = bayes.guess(['nada', 'nix'])
  >>> guess3
  []

As you can see the results above make sense. Nowlet's start to add another
pool with different concent:

  >>> _id3 = m01.mongo.getObjectId(3)
  >>> data3 = {'_id': _id3, 'text': u'Here comes more content'}
  >>> doc3 = m01.bayes.testing.Document(data3)
  >>> doc3.__name__
  u'000000030000000000000000'

  >>> bayes.train(doc3.__name__, 'more', doc3.words)
  True

  >>> _id4 = m01.mongo.getObjectId(4)
  >>> data4 = {'_id': _id4, 'text': u'And there is even more'}
  >>> doc4 = m01.bayes.testing.Document(data4)
  >>> doc4.__name__
  u'000000040000000000000000'

  >>> bayes.train(doc4.__name__, 'more', doc4.words)
  True

  >>> transaction.commit()

Now you can see we have a second pool called 'more':

  >>> printMemory(bayes.memory)
  {u'000000010000000000000000': {'__name__': u'000000010000000000000000',
                                 '_id': ObjectId('...'),
                                 '_pid': ObjectId('...'),
                                 '_type': u'BayesMemory',
                                 '_version': 1,
                                 'created': datetime.datetime(...),
                                 'data': {u'words': {u'This': 1,
                                                     u'contains': 1,
                                                     u'doc': 1,
                                                     u'dummy': 2,
                                                     u'text': 1}},
                                 'modified': datetime.datetime(...)},
   u'000000020000000000000000': {'__name__': u'000000020000000000000000',
                                 '_id': ObjectId('...'),
                                 '_pid': ObjectId('...'),
                                 '_type': u'BayesMemory',
                                 '_version': 1,
                                 'created': datetime.datetime(...),
                                 'data': {u'words': {u'This': 1,
                                                     u'dummy': 1,
                                                     u'is': 1,
                                                     u'more': 1,
                                                     u'text': 1}},
                                 'modified': datetime.datetime(...)},
   u'000000030000000000000000': {'__name__': u'000000030000000000000000',
                                 '_id': ObjectId('...'),
                                 '_pid': ObjectId('...'),
                                 '_type': u'BayesMemory',
                                 '_version': 1,
                                 'created': datetime.datetime(...),
                                 'data': {u'more': {u'Here': 1,
                                                    u'comes': 1,
                                                    u'content': 1,
                                                    u'more': 1}},
                                 'modified': datetime.datetime(...)},
   u'000000040000000000000000': {'__name__': u'000000040000000000000000',
                                 '_id': ObjectId('...'),
                                 '_pid': ObjectId('...'),
                                 '_type': u'BayesMemory',
                                 '_version': 1,
                                 'created': datetime.datetime(...),
                                 'data': {u'more': {u'And': 1,
                                                    u'even': 1,
                                                    u'is': 1,
                                                    u'more': 1,
                                                    u'there': 1}},
                                 'modified': datetime.datetime(...)}}

  >>> pprint(bayes.corpus)
  {u'And': 1,
   u'Here': 1,
   u'This': 2,
   u'comes': 1,
   u'contains': 1,
   u'content': 1,
   u'doc': 1,
   u'dummy': 3,
   u'even': 1,
   u'is': 2,
   u'more': 3,
   u'text': 2,
   u'there': 1}

  >>> pprint(bayes.pools)
  {'more': {u'And': 1,
            u'Here': 1,
            u'comes': 1,
            u'content': 1,
            u'even': 1,
            u'is': 1,
            u'more': 2,
            u'there': 1},
   'words': {u'This': 2,
             u'contains': 1,
             u'doc': 1,
             u'dummy': 3,
             u'is': 1,
             u'more': 1,
             u'text': 2}}

Now the interesting part. Let's check to which pool a list of words will fit:

  >>> bayes.guess(['This', 'dummy'])
  [('words', 0.999...)]

  >>> bayes.guess(['More', 'comes'])
  [('more', 0.999...)]

And now with text containd in both pools:

  >>> bayes.guess(['this', 'more'])
  [('more', 0.620...), ('words', 0.379...)]

Don't ask me about the calculated numbers but it makes sense what we've got
since the 'more' pool contains 2 items with the word 'more' and the 'words'
pool only one item.

Let's compare the aboe bayes with a new onw which is using the 'robinson'
instead of the 'robinson-fisher' filter:

  >>> bayes2 = m01.bayes.testing.SampleBayesContainerItem({'useRobinsonFisher': False})
  >>> container[u'bayes2'] = bayes2
  >>> bayes2 = container[u'bayes2']
  >>> bayes2
  <SampleBayesContainerItem using Robinson>

  >>> transaction.commit()

  >>> bayes2.train(doc.__name__, 'words', doc.words)
  True

  >>> bayes2.train(doc2.__name__, 'words', doc2.words)
  True

  >>> bayes2.train(doc3.__name__, 'more', doc3.words)
  True

  >>> bayes2.train(doc4.__name__, 'more', doc4.words)
  True

  >>> transaction.commit()

now compare the results:

  >>> bayes2.guess(['This', 'dummy'])
  [('words', 0.999...)]

  >>> bayes2.guess(['More', 'comes'])
  [('more', 0.999...)]

  >>> bayes2.guess(['this', 'more', ''])
  [('more', 0.620...), ('words', 0.379...)]

As you can see we've got similar results. Let's take a look at out bayes data
structure used in the BayesContainerItem:

  >>> printBayes(bayes)
  {'__name__': u'bayes',
   '_id': ObjectId('...'),
   '_pid': ObjectId('000000000000000000000000'),
   '_type': u'SampleBayesContainerItem',
   '_version': 1,
   'corpus': {u'And': 1,
              u'Here': 1,
              u'This': 2,
              u'comes': 1,
              u'contains': 1,
              u'content': 1,
              u'doc': 1,
              u'dummy': 3,
              u'even': 1,
              u'is': 2,
              u'more': 3,
              u'text': 2,
              u'there': 1},
   'corpusCounter': 20,
   'created': datetime.datetime(...),
   'memory': {u'000000010000000000000000': {'__name__': u'000000010000000000000000',
                                            '_id': ObjectId('...'),
                                            '_pid': ObjectId('...'),
                                            '_type': u'BayesMemory',
                                            '_version': 1,
                                            'created': datetime.datetime(...),
                                            'data': {u'words': {u'This': 1,
                                                                u'contains': 1,
                                                                u'doc': 1,
                                                                u'dummy': 2,
                                                                u'text': 1}},
                                            'modified': datetime.datetime(...)},
              u'000000020000000000000000': {'__name__': u'000000020000000000000000',
                                            '_id': ObjectId('...'),
                                            '_pid': ObjectId('...'),
                                            '_type': u'BayesMemory',
                                            '_version': 1,
                                            'created': datetime.datetime(...),
                                            'data': {u'words': {u'This': 1,
                                                                u'dummy': 1,
                                                                u'is': 1,
                                                                u'more': 1,
                                                                u'text': 1}},
                                            'modified': datetime.datetime(...)},
              u'000000030000000000000000': {'__name__': u'000000030000000000000000',
                                            '_id': ObjectId('...'),
                                            '_pid': ObjectId('...'),
                                            '_type': u'BayesMemory',
                                            '_version': 1,
                                            'created': datetime.datetime(...),
                                            'data': {u'more': {u'Here': 1,
                                                               u'comes': 1,
                                                               u'content': 1,
                                                               u'more': 1}},
                                            'modified': datetime.datetime(...)},
              u'000000040000000000000000': {'__name__': u'000000040000000000000000',
                                            '_id': ObjectId('...'),
                                            '_pid': ObjectId('...'),
                                            '_type': u'BayesMemory',
                                            '_version': 1,
                                            'created': datetime.datetime(...),
                                            'data': {u'more': {u'And': 1,
                                                               u'even': 1,
                                                               u'is': 1,
                                                               u'more': 1,
                                                               u'there': 1}},
                                            'modified': datetime.datetime(...)}},
   'modified': datetime.datetime(...),
   'poolCounters': {'more': 9, 'words': 11},
   'pools': {'more': {u'And': 1,
                      u'Here': 1,
                      u'comes': 1,
                      u'content': 1,
                      u'even': 1,
                      u'is': 1,
                      u'more': 2,
                      u'there': 1},
             'words': {u'This': 2,
                       u'contains': 1,
                       u'doc': 1,
                       u'dummy': 3,
                       u'is': 1,
                       u'more': 1,
                       u'text': 2}},
   'useRobinsonFisher': True}

Check if we count the words correct:

  >>> uniqueWords = set(doc.words + doc2.words + doc3.words + doc4.words)
  >>> len(bayes.corpus) == len(uniqueWords)
  True

  >>> len(bayes.pools['words']) == len(set(doc.words + doc2.words))
  True

  >>> len(bayes.pools['more']) == len(set(doc3.words + doc4.words))
  True


getPoolNames
------------

Now before we untrain our tokens, let's show some helper methods. Return a list
of pool names

  >>> bayes.getPoolNames()
  ['words', 'more']


getPoolTokens
------------

Return a list of the tokens in this pool:

  >>> bayes.getPoolTokens('words')
  [u'dummy', u'This', u'text', u'is', u'contains', u'doc', u'more']


getPoolData
-----------

Return a list of the (token, count) tuples:

  >>> pprint(bayes.getPoolData('words'))
  [(u'dummy', 3),
   (u'This', 2),
   (u'text', 2),
   (u'is', 1),
   (u'contains', 1),
   (u'doc', 1),
   (u'more', 1)]


__contains__
------------

Returns True/False if a given key is trained:

  >>> doc.__name__ in bayes
  True

  >>> 'unknown' in bayes
  False


__len__
-------

Return the pool lenght:

  >>> len(bayes)
  4


getProbs
--------

  >>> wordDict = bayes.cache['words']
  >>> tokens = ['dummy', 'This', 'more']
  >>> bayes.getProbs(tokens, wordDict)
  [0.999..., 0.999..., 0.379...]



untrain
-------

Now, start removing some documents from bayes:

  >>> bayes.untrain(doc4.__name__, 'more')
  True

And remove some without any poolName

  >>> bayes.untrain(doc3.__name__)
  True

Check our internals again and see that the doc3 and doc4 are gone from the
pools and memory dict:

  >>> printBayes(bayes)
  {'__name__': u'bayes',
   '_id': ObjectId('...'),
   '_pid': ObjectId('000000000000000000000000'),
   '_type': u'SampleBayesContainerItem',
   '_version': 1,
   'corpus': {u'This': 2,
              u'contains': 1,
              u'doc': 1,
              u'dummy': 3,
              u'is': 1,
              u'more': 1,
              u'text': 2},
   'corpusCounter': 11,
   'created': datetime.datetime(...),
   'memory': {u'000000010000000000000000': {'__name__': u'000000010000000000000000',
                                            '_id': ObjectId('...'),
                                            '_pid': ObjectId('...'),
                                            '_type': u'BayesMemory',
                                            '_version': 1,
                                            'created': datetime.datetime(...),
                                            'data': {u'words': {u'This': 1,
                                                                u'contains': 1,
                                                                u'doc': 1,
                                                                u'dummy': 2,
                                                                u'text': 1}},
                                            'modified': datetime.datetime(...)},
              u'000000020000000000000000': {'__name__': u'000000020000000000000000',
                                            '_id': ObjectId('...'),
                                            '_pid': ObjectId('...'),
                                            '_type': u'BayesMemory',
                                            '_version': 1,
                                            'created': datetime.datetime(...),
                                            'data': {u'words': {u'This': 1,
                                                                u'dummy': 1,
                                                                u'is': 1,
                                                                u'more': 1,
                                                                u'text': 1}},
                                            'modified': datetime.datetime(...)}},
   'modified': datetime.datetime(...),
   'poolCounters': {'more': 0, 'words': 11},
   'pools': {'more': {},
             'words': {u'This': 2,
                       u'contains': 1,
                       u'doc': 1,
                       u'dummy': 3,
                       u'is': 1,
                       u'more': 1,
                       u'text': 2}},
   'useRobinsonFisher': True}

  >>> transaction.commit()

And as you can see, we will get the same result like before we added the doc3
and doc4:

  >>> bayes.guess(['This', 'dummy']) == guess
  True

  >>> bayes.guess(['This', 'nada']) == guess2
  True

  >>> bayes.guess(['nada', 'nix']) == guess3
  True

Yeah, exactly the same as we've got before.

Now let's tear down our test setup:

  >>> from m01.mongo import clearThreadLocalCache
  >>> transaction.commit()
  >>> clearThreadLocalCache()

As you can see our cache items get removed:

  >>> from m01.mongo import LOCAL
  >>> pprint(LOCAL.__dict__)
  {}
