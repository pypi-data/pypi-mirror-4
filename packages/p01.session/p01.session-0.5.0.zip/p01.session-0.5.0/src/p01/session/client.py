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
$Id:$
"""
import hmac
import logging
import random
import time
try:
    from hashlib import sha1
except ImportError:
    # Python 2.4
    import sha as sha1
try:
    from email.utils import formatdate
except ImportError:
    # Python 2.4
    from email.Utils import formatdate

import zope.interface
from zope.session.interfaces import IClientId
from zope.publisher.interfaces import IRequest
from zope.publisher.interfaces.http import IHTTPApplicationRequest
from zope.schema.fieldproperty import FieldProperty
from zope.session.http import MissingClientIdException
from zope.session.http import digestEncode

from p01.session import interfaces

__docformat__ = 'restructuredtext'

logger = logging.getLogger()


class ClientId(str):
    """Client Id implementation."""
    zope.interface.implements(IClientId)
    zope.component.adapts(IRequest)

    def __new__(cls, cid):
        return str.__new__(cls, cid)


class MemcacheClientIdFactory(object):
    """Client id adapter factory managing and using cookies."""

    zope.interface.implements(interfaces.IMemcacheClientIdFactory)

    lifetime = FieldProperty(
        interfaces.IMemcacheClientIdFactory['lifetime'])
    secure = FieldProperty(interfaces.IMemcacheClientIdFactory['secure'])
    postOnly = FieldProperty(interfaces.IMemcacheClientIdFactory['postOnly'])
    domain = FieldProperty(interfaces.IMemcacheClientIdFactory['domain'])

    def __init__(self, namespace, secret, lifetime=None, domain=None,
        secure=False, postOnly=False):
        """Initialize a client id adapter.
        
        Note, this adapter must get initalized in a module and use the same
        attrs in each instance.
        
        Note, the lifetime must get changed to 0 (zero) for use an infinit
        expire time. This means such cookie will exist in a new browser after
        close the current browser. This is normaly not what you need for 
        authentication cookies.
        """
        self.namespace = namespace
        self.secret = secret
        self.lifetime = lifetime
        self.domain = domain
        self.secure = secure
        self.postOnly = postOnly

    def __call__(self, request):
        """Adapting a request returns an IClientId instance."""
        return ClientId(self.getClientId(request))

    def getClientId(self, request):
        """Get the client id."""
        sid = self.getRequestId(request)
        if sid is None:
            if self.postOnly and not (request.method == 'POST'):
                raise MissingClientIdException
            else:
                sid = self.generateUniqueId()
                self.setRequestId(request, sid)
        elif self.lifetime:
            # If we have a finite cookie lifetime, then set the cookie
            # on each request to avoid losing it.
            self.setRequestId(request, sid)

        return sid

    def generateUniqueId(self):
        """Generate a new, random, unique id."""
        data = "%.20f%.20f%.20f" % (random.random(), time.time(), time.clock())
        # BBB code for Python 2.4, inspired by the fallback in hmac
        if hasattr(sha1, '__call__'):
            digest = sha1(data).digest()
        else:
            digest = sha1.new(data).digest()
        s = digestEncode(digest)
        # we store a HMAC of the random value together with it, which makes
        # our session ids unforgeable.
        mac = hmac.new(s, self.secret, digestmod=sha1).digest()
        return s + digestEncode(mac)

    def getRequestId(self, request):
        """Return the browser id encoded in request as a string."""
        response_cookie = request.response.getCookie(self.namespace)
        if response_cookie:
            sid = response_cookie['value']
        else:
            request = IHTTPApplicationRequest(request)
            sid = request.getCookies().get(self.namespace, None)
        # If there is an id set on the response, use that but
        # don't trust it.  We need to check the response in case
        # there has already been a new session created during the
        # course of this request.
        if sid is None or len(sid) != 54:
            return None
        s, mac = sid[:27], sid[27:]
        
        # call encode() on value as a workaround a bug where the hmac
        # module only accepts str() types in Python 2.6
        if (digestEncode(hmac.new(s.encode(), self.secret, digestmod=sha1
            ).digest()) != mac):
            return None
        else:
            return sid

# XXX: optional use virtual host root instead of application root, this will
#      avoid calling notifyVirtualHostChanged event and regenerate cookies?
    def setRequestId(self, request, id):
        """Set cookie with id on request."""
        # TODO: Currently, the path is the ApplicationURL. This is reasonable,
        #     and will be adequate for most purposes.
        #     A better path to use would be that of the folder that contains
        #     the site manager this service is registered within. However,
        #     that would be expensive to look up on each request, and would
        #     have to be altered to take virtual hosting into account.
        #     Seeing as this utility instance has a unique namespace for its
        #     cookie, using ApplicationURL shouldn't be a problem.
        response = request.response
        options = {}
        if self.lifetime is not None:
            if self.lifetime:
                expires = formatdate(time.time() + self.lifetime,
                    localtime=False, usegmt=True)
            else:
                expires = 'Tue, 19 Jan 2038 00:00:00 GMT'
            options['expires'] = expires

        if self.secure:
            options['secure'] = True

        if self.domain:
            options['domain'] = self.domain
        response.setCookie(self.namespace, id, path=request.getApplicationURL(
            path_only=True), **options)

        response.setHeader('Cache-Control', 'no-cache="Set-Cookie,Set-Cookie2"')
        response.setHeader('Pragma', 'no-cache')
        response.setHeader('Expires', 'Mon, 26 Jul 1997 05:00:00 GMT')


class ThirdPartyClientIdFactory(object):
    """Client id adapter factory using third party cookies."""

    zope.interface.implements(interfaces.IThirdPartyClientIdFactory)

    namespace = FieldProperty(
        interfaces.IThirdPartyClientIdFactory['namespace'])

    def __init__(self, namespace=None):
        """Create the cookie-based client id manager"""
        self.namespace = namespace

    def __call__(self, request):
        """Adapting a request returns an IClientId instance."""
        return ClientId(self.getClientId(request))

    def getClientId(self, request):
        """Get the client id."""
        sid = self.getRequestId(request)
        if sid is None:
            raise MissingClientIdException
        return sid

    def getRequestId(self, request):
        """Return the browser id encoded in request as a string."""
        response_cookie = request.response.getCookie(self.namespace)
        if response_cookie:
            sid = response_cookie['value']
        else:
            request = IHTTPApplicationRequest(request)
            sid = request.getCookies().get(self.namespace, None)
        return sid

    def generateUniqueId(self):
        """We are not responsible for generate a cookie id."""
        logger.warning('ThirdPartyClientIdFactory is using thirdparty cookies '
                       'ignoring generateUniqueId call')

    def setRequestId(self, request, id):
        """We are not responsible for set a cookie."""
        logger.warning('ThirdPartyClientIdFactory is using thirdparty cookies '
                       'ignoring setRequestId call')


#def notifyVirtualHostChanged(event):
#    """Adjust cookie paths when IVirtualHostRequest information changes."""
#    request = IHTTPRequest(event.request, None)
#    if event.request is None:
#        return
#    cid = interfaces.IClientId(self.request)
#    for name, adapter in component.getAdaptersFor(interfaces.IClientId):
#        # Third party ClientId Managers need no modification at all
#        if not adapter.thirdparty:
#            cookie = request.response.getCookie(adapter.namespace)
#            if cookie:
#                adapter.setRequestId(request, cookie['value'])
