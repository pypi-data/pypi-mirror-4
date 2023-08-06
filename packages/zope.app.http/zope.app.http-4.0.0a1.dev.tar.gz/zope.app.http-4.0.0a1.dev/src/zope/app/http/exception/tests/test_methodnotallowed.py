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
"""Tests for HTTP error views
"""
from unittest import TestCase, TestSuite, main, makeSuite
from io import BytesIO

from zope.interface import Interface, implementer
from zope.publisher.http import HTTPRequest
from zope.publisher.interfaces.http import IHTTPRequest

from zope.component import provideAdapter


class I(Interface):
    pass


@implementer(I)
class C(object):
    pass


class GetView(object):
    def __init__(self, context, request):
        pass
    def GET(self):
        pass


class DeleteView(object):
    def __init__(self, context, request):
        pass
    def DELETE(self):
        pass


class TestMethodNotAllowedView(TestCase):

    def setUp(self):
        provideAdapter(GetView, (I, IHTTPRequest), Interface, 'GET')
        provideAdapter(DeleteView, (I, IHTTPRequest), Interface, 'DELETE')
        provideAdapter(GetView, (I, IHTTPRequest), Interface, 'irrelevant')
        provideAdapter(DeleteView, (I, IHTTPRequest), Interface, 'also_irr.')
        
        from zope.publisher.interfaces import IDefaultViewName
        from zope.publisher.interfaces.browser import IBrowserRequest
        #do the same as defaultView would for something like:
        #<defaultView
        #    for=".test_methodnotallowed.I"
        #    name="index.html"
        #    />

        provideAdapter(u'index.html', (I, IBrowserRequest), IDefaultViewName)
    
    def test(self):
        from zope.publisher.interfaces.http import MethodNotAllowed
        from zope.app.http.exception.methodnotallowed \
             import MethodNotAllowedView

        context = C()
        request = HTTPRequest(BytesIO(b'PUT /bla/bla HTTP/1.1\n\n'), {})
        error = MethodNotAllowed(context, request)
        view = MethodNotAllowedView(error, request)

        result = view()

        self.assertEqual(request.response.getStatus(), 405)
        self.assertEqual(request.response.getHeader('Allow'), 'DELETE, GET')
        self.assertEqual(result, b'Method Not Allowed')


    def test_defaultView(self):
        # do the same with a BrowserRequest
        # edge case is that if someone does a defaultView for the context object
        # but the app is not prepared for webdav or whatever
        # and someone comes with a not allowed method, the exception
        # view fails on getAdapters
        # this might be an issue with zope.publisher, as it provides
        # a unicode object with provideAdapter, but I don't think I can
        # change zope.publisher
        from zope.publisher.interfaces.http import MethodNotAllowed
        from zope.app.http.exception.methodnotallowed \
             import MethodNotAllowedView
        from zope.publisher.browser import BrowserRequest

        context = C()
        request = BrowserRequest(BytesIO(b'PUT /bla/bla HTTP/1.1\n\n'), {})

        error = MethodNotAllowed(context, request)
        view = MethodNotAllowedView(error, request)

        result = view()

        self.assertEqual(request.response.getStatus(), 405)
        #well this is empty, but we're grateful that it does not break
        self.assertEqual(request.response.getHeader('Allow'), '')
        self.assertEqual(result, b'Method Not Allowed')


def test_suite():
    return TestSuite((
        makeSuite(TestMethodNotAllowedView),
        ))

if __name__=='__main__':
    main(defaultTest='test_suite')
