##############################################################################
#
# Copyright (c) 2007 Zope Foundation and Contributors.
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
$Id: __init__.py 97 2007-03-29 22:58:27Z rineichen $
"""

import zope.interface
import zope.component
import z3c.pagelet.browser
import z3c.template.interfaces
import zope.authentication.interfaces


class SystemErrorPagelet(z3c.pagelet.browser.BrowserPagelet):
    """SystemError pagelet."""

    def isSystemError(self):
        return True


class UnauthorizedPagelet(z3c.pagelet.browser.BrowserPagelet):
    """Unauthorized pagelet."""

    def update(self):
        # Set the error status to 403 (Forbidden) in the case when we don't
        # challenge the user
        self.request.response.setStatus(403)

        # make sure that squid does not keep the response in the cache
        self.request.response.setHeader(
            'Expires', 'Mon, 26 Jul 1997 05:00:00 GMT')
        self.request.response.setHeader(
            'Cache-Control', 'no-store, no-cache, must-revalidate')
        self.request.response.setHeader('Pragma', 'no-cache')

        principal = self.request.principal
        auth = zope.component.getUtility(
            zope.authentication.interfaces.IAuthentication)
        auth.unauthorized(principal.id, self.request)

    def render(self):
        if self.request.response.getStatus() not in (302, 303):
            template = zope.component.getMultiAdapter(
                (self, self.request), z3c.template.interfaces.IContentTemplate)
            return template(self)


class UserErrorPagelet(z3c.pagelet.browser.BrowserPagelet):
    """UserError pagelet."""

    def title(self):
        return self.context.__class__.__name__


class NotFoundPagelet(z3c.pagelet.browser.BrowserPagelet):
    """NotFound pagelet."""

    def render(self):
        self.request.response.setStatus(404)
        template = zope.component.getMultiAdapter(
            (self, self.request), z3c.template.interfaces.IContentTemplate)
        return template(self)
