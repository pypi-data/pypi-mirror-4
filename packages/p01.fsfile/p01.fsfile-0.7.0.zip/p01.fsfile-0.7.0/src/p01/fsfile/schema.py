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

import zope.interface
import zope.schema
import zope.schema.interfaces
import zope.i18nmessageid
import zope.configuration.fields
from zope.schema.interfaces import SchemaNotProvided
from zope.schema.interfaces import RequiredMissing
from zope.schema.interfaces import TooSmall
from zope.schema.interfaces import TooBig

from p01.fsfile import interfaces

_ = zope.i18nmessageid.MessageFactory('p01')


class IFSFileUpload(zope.schema.interfaces.IMinMaxLen):
    """File system file upload field interface."""

    allowEmptyPostfix = zope.schema.Bool(
        title=_(u'Allow empty post fix in file name'),
        description=_(u'Allow empty post fix in filename'),
        required=False,
        default=False)

    fsStorageName = zope.schema.ASCIILine(
        title=_(u'FSStorage utility name'),
        description=_(u'FSStorage utility name'),
        required=False,
        default='')

    fsNameSpace = zope.schema.ASCIILine(
        title=_(u'FSStorage namespace'),
        description=_(u'FSStorage namespace'),
        required=False,
        default=None)

    fsFileFactory = zope.configuration.fields.GlobalObject(
        title=_(u'FSFile factory'),
        description=_(u'FSFile factory'),
        required=False,
        default=None)

    min_size = zope.schema.Int(
        title=_(u'Minimum file size'),
        description=_(u'Minimum file size'),
        min=0,
        required=False,
        default=None)

    max_size = zope.schema.Int(
        title=_(u'Maximum file size'),
        description=_(u'Maximum file size'),
        min=0,
        required=False,
        default=None)


class FSFileUpload(zope.schema.Field):
    """File system file upload field implementation."""

    zope.interface.implements(IFSFileUpload)
    """File system file upload field interface."""

    def __init__(self, allowEmptyPostfix=False, fsStorageName=None,
        fsNameSpace=None, fsFileFactory=None, min_size=0, max_size=None,
        **kw):
        self.schema = interfaces.IFSFile
        self.allowEmptyPostfix = allowEmptyPostfix
        self.fsStorageName = fsStorageName
        self.fsNameSpace = fsNameSpace
        self.fsFileFactory = fsFileFactory
        self.min_size = min_size
        self.max_size = max_size
        super(FSFileUpload, self).__init__(**kw)

    def _validate(self, value):
        super(FSFileUpload, self)._validate(value)

        # schema has to be provided by value
        if not self.schema.providedBy(value):
            raise SchemaNotProvided

        # validate size if given
        if self.min_size is not None and value.size < self.min_size:
            raise TooSmall(value, self.min_size)

        if self.max_size is not None and value.size > self.max_size:
            raise TooBig(value, self.max_size)
