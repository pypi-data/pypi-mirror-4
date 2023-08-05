###############################################################################
#
# Copyright (c) 2011 Projekt01 GmbH.
# All Rights Reserved.
#
###############################################################################
"""
$Id: testing.py 2707 2011-12-12 01:58:47Z roger.ineichen $
"""

import zope.interface
import zope.component
from zope.i18n.interfaces import IUserPreferredLanguages
from zope.i18n.interfaces import ITranslationDomain
from zope.i18n.interfaces import INegotiator
from zope.publisher.interfaces import IRequest
from zope.security import management
from zope.security.interfaces import IParticipation
from zope.security.interfaces import IPrincipal


###############################################################################
#
# test component
#
###############################################################################

class DummyNegotiator(object):

    zope.interface.implements(INegotiator)

    def getLanguage(self, languages, request):
        return request.lang


class DummyTranslationDomain(object):
    """Translation domain for testing"""

    zope.interface.implements(ITranslationDomain)

    # See zope.i18n.interfaces.ITranslationDomain
    domain = None

    def __init__(self, domain, messages=None):
        """Initializes the object"""
        self.domain = domain
        if messages is None:
            messages = {('de', 'foo'): 'Foo', ('de', 'bar'): 'Bar'}
        self.messages = messages

    def translate(self, msgid, mapping=None, context=None,
                  target_language=None, default=None):
        # Find out what the target language should be
        if target_language is None and context is not None:
            langs = [m[0] for m in self.messages.keys()]
            # Let's negotiate the language to translate to. :)
            negotiator = zope.component.getUtility(INegotiator)
            target_language = negotiator.getLanguage(langs, context)

        # Find a translation; if nothing is found, use the default
        # value
        if default is None:
            default = unicode(msgid)
        text = self.messages.get((target_language, msgid))
        if text is None:
            text = default
        return zope.i18n.interpolate(text, mapping)


###############################################################################
#
# test setup
#
###############################################################################


class Principal(object):
    """Setup principal."""

    zope.interface.implements(IPrincipal)

    id = 'roger.ineichen'
    title = u'Roger Ineichen'
    description = u'Roger Ineichen'


class Participation(object):
    """Setup configuration participation."""

    # also implement IRequest which makes session adapter available
    zope.interface.implements(IParticipation)

    def __init__(self, principal, lang):
        self.principal = principal
        self.lang = lang
        self.data = {}

    def get(self, key):
        self.data.get(key)

    def __setitem__(self, key, value):
        self.data[key] = value

    def getPreferredLanguages(self):
        return [self.lang]

    interaction = None


def newInteraction(lang='en'):
    management.endInteraction()
    principal = Principal()
    participation = Participation(principal, lang)
    management.newInteraction(participation)
    return participation


def endInteraction():
    management.endInteraction()
