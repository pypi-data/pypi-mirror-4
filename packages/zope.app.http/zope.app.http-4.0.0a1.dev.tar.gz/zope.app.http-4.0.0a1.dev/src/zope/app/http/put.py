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
"""HTTP `PUT` verb"""
__docformat__ = 'restructuredtext'

from zope.component import queryAdapter
from zope.event import notify
from zope.lifecycleevent import ObjectCreatedEvent
from zope.interface import implementer
from zope.filerepresentation.interfaces import IWriteFile
from zope.filerepresentation.interfaces import \
    IWriteDirectory, IReadDirectory, IFileFactory
import zope.traversing.browser
import zope.publisher.interfaces.http
from zope.app.http.interfaces import INullResource


@implementer(INullResource)
class NullResource(object):
    """Object representing objects to be created by a `PUT`.
    """

    def __init__(self, container, name):
        self.container = container
        self.name = name


class NullPUT(object):
    """Put handler for null resources (new file-like things)

    This view creates new objects in containers.

    """

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def PUT(self):
        request = self.request

        body = request.bodyStream
        name = self.context.name
        container = self.context.container

        # Find the extension
        ext_start = name.rfind('.')
        if ext_start > 0:
            ext = name[ext_start:]
        else:
            ext = "."

        # Get a "directory" surrogate for the container
        # TODO: Argh. Why don't we have a unioned Interface for that?!?
        dir_write = IWriteDirectory(container)
        dir_read = IReadDirectory(container)

        # Now try to get a custom factory for he container
        factory = queryAdapter(container, IFileFactory, ext)

        # Fall back to a non-custom one
        if factory is None:
            factory = IFileFactory(container, None)
        if factory is None:
            raise zope.publisher.interfaces.http.MethodNotAllowed(
                container, self.request)

        # TODO: Need to add support for large files
        data = body.read()

        newfile = factory(name, request.getHeader('content-type', ''), data)
        notify(ObjectCreatedEvent(newfile))

        dir_write[name] = newfile
        # Ickyness with non-predictable support for containment:
        #   make sure we get a containment proxy
        newfile = dir_read[name]

        request.response.setStatus(201)
        request.response.setHeader(
            'Location', zope.traversing.browser.absoluteURL(newfile, request))
        return ''


class FilePUT(object):
    """Put handler for existing file-like things

    """

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def PUT(self):
        body = self.request.bodyStream
        file = self.context
        adapter = IWriteFile(file, None)
        if adapter is None:
            raise zope.publisher.interfaces.http.MethodNotAllowed(
                self.context, self.request)

        length = int(self.request.get('CONTENT_LENGTH', -1))
        adapter.write(body.read(length))

        return ''
