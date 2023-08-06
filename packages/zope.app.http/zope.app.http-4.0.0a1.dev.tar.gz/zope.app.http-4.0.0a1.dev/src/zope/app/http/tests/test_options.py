##############################################################################
#
# Copyright (c) 2008 Zope Foundation and Contributors.
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
"""Test HTTP OPTIONS verb
"""
from unittest import TestCase, TestSuite, makeSuite

import zope.interface

from zope.publisher.browser import IBrowserRequest
from zope.publisher.browser import TestRequest

import zope.app.http.options


class IDeletable(zope.interface.Interface):
    "Marker interface that says that something understand the DELETE method"


@zope.interface.implementer(IDeletable)
class Deletable(object):
    "Rocket science implementation of IDeletable"


class DeleteView(object):
    "A view for a deletable object"
    def __init__(self, context, request):
        self.context = context
        self.request = request


class TestOptions(TestCase):

    def testDefaultMethods(self):
        dumbObj = object()

        request = TestRequest()
        options = zope.app.http.options.OPTIONS(dumbObj, request)

        self.assertEqual(options.OPTIONS(), '')
        getHeader = request.response.getHeader
        self.assertEqual(getHeader('Allow'), 'GET, HEAD, POST')
        self.assertEqual(getHeader('DAV', literal=True), '1,2')
        self.assertEqual(getHeader('MS-Author-Via', literal=True), 'DAV')
        self.assertEqual(request.response.getStatus(), 200)

    def testExtendedMethods(self):
        gst = zope.component.getGlobalSiteManager()
        gst.registerAdapter(DeleteView, (IDeletable, IBrowserRequest),
                            zope.interface.Interface, 'PUT')

        deletableObject = Deletable()

        request = TestRequest()
        options = zope.app.http.options.OPTIONS(deletableObject, request)
        self.assertEqual(options.OPTIONS(), '')
        getHeader = request.response.getHeader
        self.assertEqual(getHeader('Allow'), 'GET, HEAD, POST, PUT')


def test_suite():
    return TestSuite((
        makeSuite(TestOptions),
        ))
