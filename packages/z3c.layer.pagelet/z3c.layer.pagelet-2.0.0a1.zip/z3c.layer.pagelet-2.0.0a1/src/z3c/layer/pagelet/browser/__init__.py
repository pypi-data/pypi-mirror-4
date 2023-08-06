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
"""Browser Code.
"""
from z3c.layer.pagelet import interfaces
import z3c.pagelet.browser
import z3c.template.interfaces
import zope.authentication.interfaces
import zope.component
import zope.interface

def inDevMode():
    """Are we are running in debug mode? Can error messages be more telling?"""
    try:
        from zope.app.appsetup.appsetup import getConfigContext
    except ImportError:
        # We are outside a Zope 3 context, so let's play safe:
        return False

    config_context = getConfigContext()
    if config_context is None:
        # We are probably inside a test:
        return True
    return config_context.hasFeature('devmode')


@zope.interface.implementer(interfaces.ISystemErrorPagelet)
class SystemErrorPagelet(z3c.pagelet.browser.BrowserPagelet):
    """SystemError pagelet."""

    def update(self):
        if inDevMode():
            self.request.response.setStatus(500)


    def isSystemError(self):
        return True


@zope.interface.implementer(interfaces.IUnauthorizedPagelet)
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


@zope.interface.implementer(interfaces.IUserErrorPagelet)
class UserErrorPagelet(z3c.pagelet.browser.BrowserPagelet):
    """UserError pagelet."""

    def title(self):
        return self.context.__class__.__name__


@zope.interface.implementer(interfaces.INotFoundPagelet)
class NotFoundPagelet(z3c.pagelet.browser.BrowserPagelet):
    """NotFound pagelet."""

    def render(self):
        self.request.response.setStatus(404)
        template = zope.component.getMultiAdapter(
            (self, self.request), z3c.template.interfaces.IContentTemplate)
        return template(self)
