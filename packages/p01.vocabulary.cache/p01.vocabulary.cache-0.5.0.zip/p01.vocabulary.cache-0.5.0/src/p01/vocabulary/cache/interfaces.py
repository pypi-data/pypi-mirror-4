##############################################################################
#
# Copyright (c) 2011 Projekt01 GmbH.
# All Rights Reserved.
#
##############################################################################
"""
$Id: interfaces.py 3159 2012-11-10 10:23:28Z roger.ineichen $
"""
__docformat__ = "reStructuredText"

import zope.schema
import zope.schema.interfaces


class ICachedVocabulary(zope.schema.interfaces.IContextSourceBinder):
    """IContextSourceBinder providing a cached vocabulary per language
    
    This schema defines an API which allows to setup cached vocabularies
    and return the correct predefined vocabulary for a specific lanugage
    during bind an IContextSourceBinder

    """

    cache = zope.schema.Field(u"Vocabulary cache with language/vocabulary data")

    sort = zope.schema.Bool(
        title=u'Sort marker',
        description=u'Sort marker',
        default=False,
        required=True,
        )

    defaultLanguage = zope.schema.TextLine(
        title=u'Default Language',
        description=u'Default Language',
        default=u'en',
        required=True,
        )

    def addVocabulary(lang, vocabulary):
        """Add a new vocabulary with the given langage key"""

    def getVocabulary(lang=None):
        """Get cached or new vocabulary"""

    def __contains__(value):
        """Return whether the value is available in this source

        Support schema validation without to support ISource. The Choice field
        just calls value in self.vocabulary without bind the field even if the
        vocabulary is a IContextSourceBinder. This ends with not iterable.
        Let's just support the __contains__ method which allows to check if
        a value is a part of the vocabulary.

        """

    def __call__(context):
        """Return a context-bound instance that implements ISource.

        The returned ISource must provide the correct language. This is normaly
        done invoking a request locale by using the the guessLanguage method.
        If the guessLanguage is not able to choose the right language the 
        vocabulary for the defaultLangage should get used.

        """

    def queryTermByTitle(title, default=None):
        """Return the right term by the given title.
        
        This method is useable if we use a tagging widget and try to lookup a
        valid key for a given tag (translated title).

        NOTE: if you use this method, your cached vocabularies must implement
        the method queryTermByTitle! See: p01.vocabulary.legacy GroupTerm and
        GroupVocabulary as a sample.

        """


class ICachedSimpleVocabulary(zope.schema.interfaces.IContextSourceBinder):
    """IContextSourceBinder providing a cached vocabulary per language
    
    This schema offers an enhance API which allows to populate new 
    SimpleVocabulary instances during bind an IContextSourceBinder.

    """

    cache = zope.schema.Field(u"Vocabulary cache with language/vocabulary data")
    vocabulary = zope.schema.Field(u"Vocabulary providing simple i18n terms")
    vocabularyFactory = zope.schema.Field(u"Optional vocabulary factory class")
    termFactory = zope.schema.Field(u"Optional term factory class")

    sort = zope.schema.Bool(
        title=u'Sort marker',
        description=u'Sort marker',
        default=False,
        required=True,
        )

    defaultLanguage = zope.schema.TextLine(
        title=u'Default Language',
        description=u'Default Language',
        default=u'en',
        required=True,
        )

    def getTerm(term, lang):
        """Create a new term based on the given term and translated title"""

    def sortTerms(terms):
        """Sort given terms"""

    def quessLanguage():
        """Guess the language, by default based on request and INegotiator"""

    def ensureVocabulary(lang):
        """Ensure new vocabulary for caching"""

    def getVocabulary(lang=None):
        """Get cached or new vocabulary"""

    def __contains__(value):
        """Return whether the value is available in this source

        Support schema validation without to support ISource. The Choice field
        just calls value in self.vocabulary without bind the field even if the
        vocabulary is a IContextSourceBinder. This ends with not iterable.
        Let's just support the __contains__ method which allows to check if
        a value is a part of the vocabulary.

        """

    def __call__(context):
        """Adapt context and return vocabulary"""
