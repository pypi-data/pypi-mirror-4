##############################################################################
#
# Copyright (c) 2011 Projekt01 GmbH.
# All Rights Reserved.
#
##############################################################################
"""
$Id: vocabulary.py 3128 2012-09-27 02:07:57Z roger.ineichen $
"""
__docformat__ = "reStructuredText"

import zope.interface
import zope.i18n
from zope.schema import vocabulary
import zope.security.management

from p01.vocabulary.cache import interfaces


# interaction participation
def queryRequest():
    participation = None
    interaction = zope.security.management.queryInteraction()
    if interaction is not None:
        participation = interaction.participations[0]
    return participation


class RequestLookupMixin(object):
    """Request lookup mixin class
    
    This mixin class provides a request lookup concept based on a security
    interaction. The method guessLanguage provides the language lookup without
    an explicit given request. Because the vocabulary usage is not based on
    requests. By default the defaultLanguage get used

    IMPORTANT:
    This concept is based on zope.i18n language negotiation which uses by
    default an environment key called zope_i18n_allowed_languages which defines
    allowed languages. I guess you are not using the zope default concept which
    is based on different reason not usable. If so, implement your own concept
    in the guessLanguage method. Here is the code which by default uses the
    environ key found in zope.i18n.config:
    
      ALLOWED_LANGUAGES_KEY = 'zope_i18n_allowed_languages'
      ALLOWED_LANGUAGES = os.environ.get(ALLOWED_LANGUAGES_KEY, None) 

    I recommend to use a pattern which defines the offered languages in your
    project and makes use of then in a customized INegotiator. You could also
    implement a much more enhanced pattern and offer the cached negotiated
    language directly accessible from the request.
    
    btw, the reason why the default zope concept is not very usable is, that
    the offered languages get implicit defined by the installed catalog
    languages. This means you can't really restrict one site or another to
    some offered languages.

    """

    defaultLanguage = 'en'

    def quessLanguage(self, request=None):
        """Guess the language, by default based on request and INegotiator"""
        if request is None:
            request = queryRequest()
        if request is not None:
            lang = zope.i18n.negotiate(request)
        else:
            # testing cases usually
            lang = self.defaultLanguage
        return lang


class CachedVocabulary(RequestLookupMixin):
    """Cached source factory which uses a dict with lang/vocabulary as input
    
    The given dict defines language/vocabulary as key/values for setup the 
    vocabulary cache. This means each vocabulary must provide translated term
    titles.

    """

    zope.interface.implements(interfaces.ICachedVocabulary)

    __name__ = None

    def __init__(self, data, defaultLanguage='en'):
        self.cache = {}
        for lang, vocabulary in data.items():
            self.cache[lang] = vocabulary
        if defaultLanguage not in data:
            raise ValueError("The data dict must provide at least the default "
                             "language vocabulary")
        self.defaultLanguage = defaultLanguage

    def addVocabulary(self, lang, vocabulary):
        """Add a new vocabulary with the given langage key"""
        self.cache[lang] = vocabulary

    def getVocabulary(self, lang=None, request=None, context=None):
        """Get cached or new vocabulary
        
        The context attribute is not used in this implementation. But required
        if you implement a site dependent caching concept.
        """
        if lang is None:
            lang = self.quessLanguage(request)
        try:
            return self.cache[lang]
        except KeyError:
            return self.cache[self.defaultLanguage]

    def __contains__(self, value):
        """Return whether the value is available in this source

        Support schema validation without to support ISource. The Choice field
        just calls value in self.vocabulary without bind the field even if the
        vocabulary is a IContextSourceBinder. This ends with not iterable.
        Let's just support the __contains__ method which allows to check if
        a value is a part of the vocabulary.

        """
        # note, it doesn't matter which language we will lookup
        return value in self.getVocabulary()

    def __call__(self, context=None):
        """Return a context-bound instance that implements ISource."""
        return self.getVocabulary(context=context)

    def queryTermByTitle(self, title, default=None):
        """Return the right term by the given title.
        
        This method is useable if we use a tagging widget and try to lookup a
        valid key for a given tag (translated title).
        """
        # lookup given title in all terms
        for vocab in self.cache.values():
            try:
                return vocab.queryTermByTitle(title)
            except AttributeError, e:
                raise AttributeError(
                    "Vocabulary %s must implement queryTermByTitle" % \
                        self.__class__.__name__)
            except (KeyError, LookupError), e:
                pass
        return default

    def __repr__(self):
        return '<%s providing %s>' % (self.__class__.__name__,
            ', '.join(self.cache.keys()))


class CachedSimpleVocabulary(RequestLookupMixin):
    """Vocabulary factory which uses an existing SimpleVocabulary as input
    
    This class returns a translated vocabulary based on the request language
    and will cache the new created SimpleVocabulary.

    This class provides different hooks and factories for create the new
    translated vocabulary. The important part is, that the given vocabulary,
    vocabularyFactory and termFactory do not provide i18n support. Only the
    terms used in the initial vocabulary input must provide i18n aware message
    ids as term title.

    Here is a sample usage:

      import os.path
      from p10.vocabulary.legacy.vocabulary import CSVVocabulary
      from my.package.i18n import MessageFactory as _

      educationVocabularyData = CSVVocabulary(
          os.path.join('path-to-educations.csv'), messageFactory=_)

      educationVocabulary = CachedSimpleVocabulary(educationVocabularyData)

    The first time a new language get used the vocabulary will setup a new
    vocabulary with translated terms and return them. You can warm up a cache
    with the following concept:
    
      educationVocabularyData = CSVVocabulary(
          os.path.join('path-to-educations.csv'), messageFactory=_)

      educationVocabulary = CachedSimpleVocabulary(educationVocabularyData)
      educationVocabulary.ensureVocabulary('en')
      educationVocabulary.ensureVocabulary('de')
      educationVocabulary.ensureVocabulary('fr')

    """

    zope.interface.implements(interfaces.ICachedSimpleVocabulary)

    __name__ = None

    def __init__(self, vocabulary, vocabularyFactory=None, termFactory=None,
        defaultLanguage='en'):
        self.cache = {}
        self.vocabulary = vocabulary
        self.vocabularyFactory = vocabularyFactory
        if termFactory is None:
            termFactory = zope.schema.vocabulary.SimpleTerm
        self.termFactory = termFactory
        self.defaultLanguage = defaultLanguage

    def getTerm(self, term, lang):
        """Create a new term based on the given term and translated title"""
        title = zope.i18n.translate(term.title, target_language=lang,
            default=term.title)
        return self.termFactory(term.value, term.token, title)

    def ensureVocabulary(self, lang):
        """Ensure new vocabulary for caching"""
        terms = [self.getTerm(term, lang) for term in list(self.vocabulary)]
        if self.vocabularyFactory is None:
            vocab = self.vocabulary.__class__(terms)
        else:
            vocab = self.vocabularyFactory([terms])
        self.cache[lang] = vocab

    def getVocabulary(self, lang=None, request=None, context=None):
        """Get cached or new vocabulary
        
        The context attribute is not used in this implementation. But required
        if you implement a site dependent caching concept.
        """
        if lang is None:
            lang = self.quessLanguage(request)
        try:
            return self.cache[lang]
        except KeyError:
            self.ensureVocabulary(lang)
        return self.cache[lang]

    def __contains__(self, value):
        """Return whether the value is available in this source

        Support schema validation without to support ISource. The Choice field
        just calls value in self.vocabulary without bind the field even if the
        vocabulary is a IContextSourceBinder. This ends with not iterable.
        Let's just support the __contains__ method which allows to check if
        a value is a part of the vocabulary.

        """
        return value in self.getVocabulary()

    def __call__(self, context):
        """Return a context-bound instance that implements ISource."""
        return self.getVocabulary(context=context)

    def __repr__(self):
        return '<%s providing %s>' % (self.__class__.__name__,
            ', '.join(self.cache.keys()))
