Vocabulary
----------

This package provides a caching concept for simple vocabularies with 
translatable terms.

  >>> import zope.component
  >>> import zope.i18n
  >>> import zope.i18n.interfaces
  >>> import zope.i18n.translationdomain
  >>> import zope.i18nmessageid
  >>> import zope.schema.vocabulary
  >>> import p01.vocabulary.cache
  >>> from p01.vocabulary.cache import testing

Make sure we provide an environment variables

  >>> import os
  >>> import zope.i18n.config
  >>> zope.i18n.config.ALLOWED_LANGUAGES
  frozenset(['de', 'en'])


setup
-----

First let's setup a translation domain:

  >>> msgs = {('de', 'car'): u'Auto',
  ...         ('de', 'wood'): u'Holz',
  ...         ('en', 'car'): u'Car',
  ...         ('en', 'wood'): u'Wood'}
  >>> domain = testing.DummyTranslationDomain('test', msgs)
  >>> zope.component.provideUtility(domain, name='test')

  >>> negotiator = testing.DummyNegotiator()
  >>> zope.component.provideUtility(negotiator)

Now define a MessageFactory:

  >>> _test_ = zope.i18nmessageid.MessageFactory('test')

  >>> car = _test_('car')
  >>> car
  u'car'

  >>> car.domain
  'test'

Now let's test our messages:

  >>> zope.i18n.translate(car, target_language='de')
  u'Auto'

Now let's setup and test our test interaction (request):

  >>> request = testing.newInteraction('de')
  >>> zope.i18n.negotiate(request)
  'de'


CachedVocabulary
----------------

Now let's define some cachable simple vocabulary:

  >>> car = _test_(u'car')
  >>> wood = _test_(u'wood')

  >>> enCar = zope.i18n.translate(car, target_language='en')
  >>> enWood = zope.i18n.translate(wood, target_language='en')
  >>> enVocab = zope.schema.vocabulary.SimpleVocabulary([
  ...    zope.schema.vocabulary.SimpleTerm('car', title=enCar),
  ...    zope.schema.vocabulary.SimpleTerm('wood', title=enWood)
  ...    ])

  >>> deCar = zope.i18n.translate(car, target_language='de')
  >>> deWood = zope.i18n.translate(wood, target_language='de')
  >>> deVocab = zope.schema.vocabulary.SimpleVocabulary([
  ...    zope.schema.vocabulary.SimpleTerm('car', title=deCar),
  ...    zope.schema.vocabulary.SimpleTerm('wood', title=deWood)
  ...    ])

  >>> vocabData = {'de': deVocab, 'en': enVocab}

And setup the real vocabulary containing our cacheble vocabulary:

  >>> cachedVocab = p01.vocabulary.cache.CachedVocabulary(vocabData)
  >>> cachedVocab
  <CachedVocabulary providing de, en>


__call__
--------

By default our cached vocabulary is adaptable by a context or None:

  >>> vocab = cachedVocab()
  >>> vocab
  <zope.schema.vocabulary.SimpleVocabulary object at ...>

  >>> for term in vocab:
  ...     print '%s: %s' % (term.value, term.title)
  car: Auto
  wood: Holz


getTerm
-------

and we can get a term:

  >>> term = vocab.getTerm('car')
  >>> term
  <zope.schema.vocabulary.SimpleTerm object at ...>

  >>> term.value
  'car'

  >>> term.token
  'car'

  >>> term.title
  u'Auto'

Now let's test our cached vocabulary with the other language:

  >>> request = testing.newInteraction('en')
  >>> vocab = cachedVocab(request)
  >>> term = vocab.getTerm('car')
  >>> term.title
  u'Car'


tear down interaction:

  >>> testing.endInteraction()
