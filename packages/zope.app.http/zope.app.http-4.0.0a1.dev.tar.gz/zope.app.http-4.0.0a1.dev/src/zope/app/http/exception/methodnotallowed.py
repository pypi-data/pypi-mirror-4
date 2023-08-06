##############################################################################
# Copyright (c) 2003 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
##############################################################################
"""HTTP 405: Method Not Allowed view
"""
from zope.component import getAdapters
from zope.interface import Interface
from zope.publisher.interfaces.http import IMethodNotAllowed


class MethodNotAllowedView(object):
    """A view for MethodNotAllowed that renders a HTTP 405 response."""

    __used_for__ = IMethodNotAllowed

    def __init__(self, error, request):
        self.error = error
        self.request = request
        allow = []

        try:
            # see test_methodnotallowed.TestMethodNotAllowedView.test_defaultView
            # I could not solve this with a while ... next() iterator
            # because it seems like once the generator had an exception it
            # stops returning items
            self.allow = [
                name for name, adapter
                in getAdapters((error.object, error.request), Interface)
                if hasattr(adapter, name)]
            self.allow.sort()
        except TypeError:
            self.allow = []

    def __call__(self):
        self.request.response.setHeader('Allow', ', '.join(self.allow))
        self.request.response.setStatus(405)
        return b'Method Not Allowed'
