##############################################################################
#
# Copyright (c) 2003 Zope Foundation and Contributors.
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
"""Not found Exception
"""
__docformat__ = 'restructuredtext'

from zope.publisher.interfaces.http import IHTTPException
from zope.interface import implementer

@implementer(IHTTPException)
class NotFound(object):

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        if self.request.method in ['MKCOL'] and \
               self.request.getTraversalStack():
            # MKCOL with non-existing parent.
            self.request.response.setStatus(409)
        else:
            self.request.response.setStatus(404)
        return b''

    __str__ = __call__
