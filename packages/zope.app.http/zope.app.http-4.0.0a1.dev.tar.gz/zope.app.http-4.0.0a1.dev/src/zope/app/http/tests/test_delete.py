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
"""Test HTTP DELETE verb
"""
from unittest import TestCase, TestSuite, makeSuite

from zope.interface import implementer
from zope.publisher.browser import TestRequest
from zope.filerepresentation.interfaces import IWriteDirectory, IFileFactory

import zope.app.http.delete
from zope.container.contained import contained
from zope.publisher.interfaces.http import MethodNotAllowed

class UnwritableContainer(object):
    pass


@implementer(IWriteDirectory, IFileFactory)
class Container(object):

    def __delitem__(self, name):
        delattr(self, name)


class TestDelete(TestCase):

    def test(self):
        container = Container()
        container.a = 'spam'
        item = contained(Container(), container, name='a')

        request = TestRequest()
        delete = zope.app.http.delete.DELETE(item, request)
        self.assert_(hasattr(container, 'a'))
        self.assertEqual(delete.DELETE(), '')
        self.assert_(not hasattr(container, 'a'))

    def test_not_deletable(self):
        container = UnwritableContainer()
        container.a = 'spam'
        item = contained(UnwritableContainer(), container, name='a')
        request = TestRequest()
        delete = zope.app.http.delete.DELETE(item, request)
        self.assertRaises(MethodNotAllowed, delete.DELETE)


def test_suite():
    return TestSuite((
        makeSuite(TestDelete),
        ))
