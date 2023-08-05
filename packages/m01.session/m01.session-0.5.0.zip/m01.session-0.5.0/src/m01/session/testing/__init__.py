###############################################################################
#
# Copyright (c) 2007 Projekt01 GmbH.
# All Rights Reserved.
#
###############################################################################
"""
$Id: __init__.py 3385 2012-11-18 14:37:45Z roger.ineichen $
"""

import os.path

import zope.interface
import zope.component
from zope.i18n.interfaces import IUserPreferredLanguages
from zope.publisher.interfaces import IRequest
from zope.security import management
from zope.security.interfaces import IParticipation
from zope.security.interfaces import IPrincipal
from zope.session.interfaces import IClientId

import m01.mongo.pool
import m01.mongo.testing
import m01.stub.testing

import m01.session.client
from m01.session import interfaces

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


def startInteraction():
    principal = Principal()
    participation = Participation(principal)
    management.newInteraction(participation)


def endInteraction():
    management.endInteraction()


def setUpSessionClientId():
    namespace = 'm01_session_testing'
    secret = 'very secure'
    cid = m01.session.client.ClientIdFactory(namespace, secret)
    zope.component.provideAdapter(cid, (IRequest,), provides=IClientId)


# empty mongodb
def setUpMongoDB(test=None):
    host = 'localhost'
    port = 45017
    sandBoxDir = os.path.join(os.path.dirname(__file__), 'sandbox')
    m01.stub.testing.startMongoDBServer(host, port, sandBoxDir=sandBoxDir)
    p = m01.mongo.pool.MongoConnectionPool(host, port)
    m01.mongo.testing._testConnection = p.connection
    p.connection.disconnect()

def tearDownMongoDB(test=None):
    m01.stub.testing.stopMongoDBServer(sleep=5.0)
    m01.mongo.testing._testConnection = None
