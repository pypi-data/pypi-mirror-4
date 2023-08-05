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
$Id: interfaces.py 3071 2012-09-05 10:39:00Z roger.ineichen $
"""
__docformat__ = "reStructuredText"

import re

import zope.interface
import zope.schema
from transaction.interfaces import IDataManager
from zope.interface.common.mapping import IReadMapping, IWriteMapping

import m01.mongo.interfaces


class ISessionStorage(m01.mongo.interfaces.IMongoContainer):
    """Session storage which knows how to get/set session items
    
    This session storage is responsible for fetch and commit the session
    to the mongodb. A session directly implements what it needs to and is
    managed by this session storage. The session item get marked as changed
    if a session item value get changed or if the session item commitInterval
    is reached.

    """

    collection = zope.interface.Attribute("""A mongoDB collection.""")

    cid = zope.schema.TextLine(
        title=u"client id",
        readonly=True)

    def createSession(key, md5Key):
        """Create a session based on the given keys"""


class IKnownSessionStorage(ISessionStorage):
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


class ISession(m01.mongo.interfaces.IMongoContainerItem):
    """Mongo storage item based session

    This is only a base class. You need to implement your own session item.

    """


class IClientIdFactory(zope.interface.Interface):
    """Client id manager managing and using cookies."""

    namespace = zope.schema.ASCIILine(
        title=u"Cookie Name",
        description=u"Name of cookie used to maintain state. "
                    u"Must be unique to the site domain name, and only "
                    u"contain ASCII letters, digits and '_'",
        required=True,
        min_length=1,
        max_length=30,
        constraint=re.compile("^[\d\w_]+$").search)

    lifetime = zope.schema.Int(
        title=u"Cookie Lifetime",
        description=u"Number of seconds until the browser expires the "
                    u"cookie. Leave blank expire the cookie when the "
                    u"browser is quit. Set to 0 to never expire.",
        min=0,
        required=False,
        default=None,
        missing_value=None)

    domain = zope.schema.TextLine(
        title=u"Effective domain",
        description=u"An identification cookie can be restricted to a "
                    u"specific domain using this option. This option sets "
                    u"the ``domain`` attributefor the cookie header. It is "
                    u"useful for setting one identification cookie for "
                    u"multiple subdomains. So if this option is set to "
                    u"``.example.org``, the cookie will be available for "
                    u"subdomains like ``yourname.example.org``. "
                    u"Note that if you set this option to some domain, the "
                    u"identification cookie won't be available for other "
                    u"domains, so, for example you won't be able to login "
                    u"using the SessionCredentials plugin via another "
                    u"domain.",
        required=False)

    secure = zope.schema.Bool(
        title=u"Request Secure communication",
        required=False,
        default=False)

    secret = zope.schema.TextLine(
        title=u"Secret",
        required=False,
        default=u'')

    postOnly = zope.schema.Bool(
        title=u"Only set cookie on POST requests",
        required=False,
        default=False)


class IThirdPartyClientIdFactory(zope.interface.Interface):
    """Client id manager using only thirdparty cookies.

    Servers like Apache or Nginx have capabilities to issue identification
    cookies. If third party cookies are beeing used, Zope will never send a
    cookie back, just check for them. You only have to make sure that this
    client id manager and the server are using the same cookie namspace.

    """

    namespace = zope.schema.TextLine(
        title=u"Cookie Name",
        description=u"Name of cookie used to maintain state. "
                    u"Must be unique to the site domain name, and only "
                    u"contain ASCII letters, digits and '_'",
        required=True,
        min_length=1,
        max_length=30,
        constraint=re.compile("^[\d\w_]+$").search)
