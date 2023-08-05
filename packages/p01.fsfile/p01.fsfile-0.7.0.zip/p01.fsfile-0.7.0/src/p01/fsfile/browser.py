##############################################################################
#
# Copyright (c) 2008 Projekt01 GmbH and Contributors.
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
__docformat__ = "reStructuredText"

from datetime import datetime

import zope.interface
import zope.component
import zope.datetime
from zope.dublincore.interfaces import IZopeDublinCore
from zope.publisher import browser
from zope.publisher.interfaces.http import IHTTPRequest
from zope.publisher.interfaces.http import IResult
from zope.security.proxy import removeSecurityProxy

from p01.fsfile import interfaces


def getFSFileResult(fsFile, request, blocksize=32768):
    """Prepare a FSFile result and apply header infos to response."""

    fsFile = removeSecurityProxy(fsFile)

    # set Content-Length
    request.response.setHeader('Content-Length', str(fsFile.size))

    # set Content-Type
    request.response.setHeader('Content-Type', fsFile.contentType)

    # set Last-Modified
    try:
        modified = IZopeDublinCore(fsFile).modified
    except TypeError:
        modified = None

    if modified is not None and isinstance(modified, datetime):
        lmt = zope.datetime.time(modified.isoformat())

        # return cache header if asked for and no newer data available
        header = request.getHeader('If-Modified-Since', None)
        if header is not None:
            header = header.split(';')[0]
            try:
                mod_since = long(zope.datetime.time(header))
            except:
                mod_since = None
            if mod_since is not None and lmt <= mod_since:
                request.response.setStatus(304)
                return ''

        request.response.setHeader('Last-Modified', 
            zope.datetime.rfc1123_date(lmt))

    # get the file reader which acts as an open file in read mode
    fileReader = interfaces.IFSFileReader(fsFile)

    # wrap our IFSFileReader into the given wrapper
    wrapper = request.environment.get('wsgi.file_wrapper', None)
    if wrapper is not None:
        return wrapper(fileReader, fileReader.readBlockSize)

    # return our file reader adapter
    return fileReader


@zope.component.adapter(interfaces.IFSFile, IHTTPRequest)
@zope.interface.implementer(IResult)
def FSFileResult(fsFile, request):
    """Provides a IResult if we directly return a IFSFile as result."""
    return getFSFileResult(fsFile, request)


class FSFileDownload(browser.BrowserPage):
    """Download view for IFSFile."""

    blocksize = 32768

    def getFSFile(self):
        return self.context

    def __call__(self):
        """Supports data download."""
        fsFile = self.getFSFile()
        # get an IResult for IFSFile. We could also return the fsFile here, but
        # this whould end in calling the IResult adapter for (IFSFile, request)
        return getFSFileResult(fsFile, self.request, self.blocksize)
