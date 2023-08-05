###############################################################################
#
# Copyright (c) 2007 Projekt01 GmbH.
# All Rights Reserved.
#
###############################################################################
"""
$Id: __init__.py 737 2007-11-18 22:24:11Z roger.ineichen $
"""

import zope.interface
from zope.i18n.interfaces import IUserPreferredLanguages
from zope.publisher.interfaces import IRequest
from zope.security import management
from zope.security.interfaces import IParticipation
from zope.security.interfaces import IPrincipal
from zope.session.interfaces import IClientId

from p01.session import interfaces
from p01.session import client
from p01.session import session


###############################################################################
#
# Test Component
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
    zope.interface.implements(IParticipation, IUserPreferredLanguages, IRequest)

    def __init__(self, principal, langs=('en', 'de')):
        self.principal = principal
        self.langs = langs
        self.annotations = {}
        self.data = {}

    def get(self, key):
        self.data.get(key)

    def __setitem__(self, key, value):
        self.data[key] = value

    def getPreferredLanguages(self):
        return self.langs

    interaction = None


def setUpMemcacheClientId():
    namespace = 'zope3_cs_123'
    secret = 'very secure'
    mcim = client.MemcacheClientIdFactory(namespace, secret)
    zope.component.provideAdapter(mcim, (IRequest,), provides=IClientId)


def setUpSession():
    zope.component.provideAdapter(session.Session, (IRequest,),
        interfaces.ISession)


def startInteraction():
    principal = Principal()
    participation = Participation(principal)
    management.newInteraction(participation)


def endInteraction():
    management.endInteraction()
