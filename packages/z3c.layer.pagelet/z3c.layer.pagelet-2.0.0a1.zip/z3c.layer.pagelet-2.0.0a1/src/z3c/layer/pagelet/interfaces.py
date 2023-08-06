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
"""Pagelet Layer Interfaces
"""
import zope.interface
import zope.browser.interfaces


class IUnauthorizedPagelet(zope.interface.Interface):
    """Unauthorized pagelet marker."""


class ISystemErrorPagelet(zope.browser.interfaces.ISystemErrorView):
    """System error view pagelet marker."""


class IUserErrorPagelet(zope.interface.Interface):
    """User error pagelet marker."""


class INotFoundPagelet(zope.interface.Interface):
    """NotFound pagelet marker."""
