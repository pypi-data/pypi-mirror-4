##############################################################################
#
# Copyright (c) 2009 Projekt01 GmbH and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""
$Id: tests.py 3385 2012-11-18 14:37:45Z roger.ineichen $
"""
__docformat__ = "reStructuredText"

import unittest
import doctest
from cStringIO import StringIO
from zope.publisher.http import HTTPRequest
#from zope.testing import doctest
from zope.testing.doctestunit import DocFileSuite
from zope.session.interfaces import IClientId

import z3c.testing

import m01.mongo.testing
import m01.session.client
import m01.session.session
import m01.session.testing
from m01.session import interfaces


class ClientIdTest(z3c.testing.InterfaceBaseTest):

    def getTestInterface(self):
        return IClientId

    def getTestPos(self):
        return ('foo',)

    def getTestClass(self):
        return m01.session.client.ClientId


class ClientIdFactoryTest(z3c.testing.InterfaceBaseTest):

    def getTestInterface(self):
        return interfaces.IClientIdFactory

    def getTestPos(self):
        return ('namespace', 'secret')

    def getTestClass(self):
        return m01.session.client.ClientIdFactory


class ThirdPartyClientIdFactoryTest(z3c.testing.InterfaceBaseTest):

    def getTestInterface(self):
        return interfaces.IThirdPartyClientIdFactory

    def getTestPos(self):
        return (u'namespace',)

    def getTestClass(self):
        return m01.session.client.ThirdPartyClientIdFactory



def test_suite():
    return unittest.TestSuite((
        doctest.DocFileSuite('README.txt',
            setUp=m01.session.testing.setUpMongoDB,
            tearDown=m01.session.testing.tearDownMongoDB,
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS),
        doctest.DocFileSuite('client.txt',
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS),
        unittest.makeSuite(ClientIdTest),
        unittest.makeSuite(ClientIdFactoryTest),
        unittest.makeSuite(ThirdPartyClientIdFactoryTest),
    ))


if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
