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
$Id: session.py 3098 2012-09-12 22:47:58Z roger.ineichen $
"""
__docformat__ = "reStructuredText"

import datetime
import thread
from hashlib import md5

import zope.interface
import zope.component
from zope.authentication.interfaces import IUnauthenticatedPrincipal
from zope.publisher.interfaces import IRequest
from zope.session.interfaces import IClientId

import m01.mongo.base
import m01.mongo.item
from m01.mongo import UTC
from m01.session import interfaces


class SessionStorage(m01.mongo.base.MongoContainerBase):
    """Session storage which knows how to get/set session items
    
    This session storage is responsible for fetch and commit the session
    to the mongodb. A session directly implements what it needs to and is
    managed by this session storage. The session item get marked as changed
    if a session item value get changed or if the session item commitInterval
    is reached.

    """

    _cid = None

    zope.interface.implements(interfaces.ISessionStorage)

    def __init__(self, request):
        """Setup storage with given client id"""
        self.request = request

    @property
    def cid(self):
        if self._cid is None:
            self._cid = str(IClientId(self.request))
        return self._cid

    @property
    def collection(self):
        """Returns a mongodb collection"""
        raise NotImplementedError(
            "Subclass must implement collection attribute")

    @property
    def cacheKey(self):
        return 'm01.session.%s.%s' % (self.cid, thread.get_ident())

    def createSession(self, key, md5Key):
        """Create a session based on the given key"""
        raise NotImplementedError("Subclass must implement load")

    def __getitem__(self, key):
        m = md5('%s.%s' % (self.cid, key))
        md5Key = unicode(m.hexdigest())
        try:
            obj = super(SessionStorage, self).__getitem__(md5Key)
        except KeyError, e:
            obj = self.createSession(key, md5Key)
            super(SessionStorage, self).__setitem__(md5Key, obj)
        return obj


class KnownSessionStorage(SessionStorage):
    """Session storage with known session keys
    
    A known session storage uses a known key for each users session which could
    get invalidated from another thread/process. This could be usefull if you
    need to implement a message system where a user will add messages for other
    users.

    Note: you need to make sure if a user get logged in and will get another
    client id that the session data get moved from the old key to the new one.
    Normaly this is done with an event subscriber for 
    IAuthenticatedPrincipalCreated events if your IAuthentication concept
    supports such an event notification.
    
    This concept doesn't expose the real used key in the mongodb. We still use
    a md5 hash as key. See the __getitem__ method.

    """

    zope.interface.implements(interfaces.IKnownSessionStorage)

    @property
    def cid(self):
        if self._cid is None:
            if IUnauthenticatedPrincipal.providedBy(self.request.principal):
                self._cid = str(IClientId(self.request))
            else:
                self._cid = self.request.principal.id
        return self._cid


class Session(m01.mongo.item.MongoContainerItem):
    """Mongo storage item based session

    This is only a base class. You need to implement your own session item.

    Note: you can wipe out expired session data by compare the last modified
    datetime within a background task. See m01.remote for a background
    task scheduler based on mongodb. Anyway you can use something like:
    
    now = datetime.datetime.now(UTC)
    lastModified = now - datetime.timedelta(seconds=60*60*2)
    # get session collection
    collection = xcore.mongo.getMongoSessionsCollection()
    # remove session which get last modified 2 hours ago from now
    collection.remove({'modified': {'$lt': lastModified}}

    """

    _m_changed_value = None
    _m_commit_delta = datetime.timedelta(seconds=60*5)

    # built in skip and dump names
    _skipNames = []
    _dumpNames = ['_id', '_pid', '_type', '_version', '__name__',
                  'created', 'modified']

    @apply
    def _m_changed():
        def fget(self):
            if not self._m_changed_value and self.modified is not None and \
                self.modified + self._m_commit_delta < \
                datetime.datetime.now(UTC):
                # mark item as changed and force commit if commitInterval is
                # reached
                self._m_changed_value = True
            return self._m_changed_value
        def fset(self, value):
            self._m_changed_value = value
        return property(fget, fset)
