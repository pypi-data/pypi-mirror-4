###############################################################################
#
# Copyright (c) 2012 Projekt01 GmbH and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
###############################################################################
"""
$Id: schema.py 3048 2012-09-02 05:33:38Z roger.ineichen $
"""
__docformat__ = "reStructuredText"

import os

import zope.interface
import zope.schema
import zope.schema.interfaces
import zope.i18nmessageid

import m01.fs.exceptions

_ = zope.i18nmessageid.MessageFactory('p01')


def getCleanFileName(filename):
    """Strip path from filenme (could happen in IE)"""
    cleanFileName = filename.split('\\')[-1]
    return cleanFileName.split('/')[-1]

def validateFileNameExtension(fileName):
    """Check missing file name extension"""
    # strip out the path section even if we do not remove them
    # later, because we just need to check the filename extension.
    dottedParts = fileName.split('.')
    if len(dottedParts) <= 1:
        raise m01.fs.exceptions.MissingFileNameExtension()

def validateAllowedFormat(fileName, allowedFormats):
    if not '*' in allowedFormats:
        postfix = fileName.split('.')[-1].lower()
        if postfix not in allowedFormats:
            v = _('Files ending with "$postfix" are not allowed.',
                  mapping={'postfix': postfix})
            raise m01.fs.exceptions.AllowedFormatError(fileName)

def validateFileSize(f, fileName, minSize, maxSize):
    fSize = os.fstat(f.fileno()).st_size
    if minSize and minSize > fSize:
        raise m01.fs.exceptions.TooSmallFile(fileName)
    if maxSize and maxSize < fSize :
        raise m01.fs.exceptions.TooBigFile(fileName)


# IFile upload schema field
class IFileUpload(zope.schema.interfaces.IField):
    """File upload field interface."""

    minSize = zope.schema.Int(
        title=_(u'Minimum file size'),
        description=_(u'Minimum file size'),
        min=0,
        required=False,
        default=None)

    maxSize = zope.schema.Int(
        title=_(u'Maximum file size'),
        description=_(u'Maximum file size'),
        min=0,
        required=False,
        default=None)

    allowedFormats = zope.schema.Tuple(
        title=_(u'Allowed Formats'),
        description=_(u'Allowed Formats'),
        default=(u'*',),
        required=True)


class FileUpload(zope.schema.Field):
    """File upload field implementation."""

    zope.interface.implements(IFileUpload)

    def __init__(self, allowedFormats='*', minSize=0, maxSize=None, **kw):
        self.allowedFormats = allowedFormats
        self.minSize = minSize
        self.maxSize = maxSize
        super(FileUpload, self).__init__(**kw)

    def validateFileNameExtension(self, fileName):
        """Validate allowed format"""
        validateFileNameExtension(fileName)

    def validateAllowedFormat(self, fileName, allowedFormats):
        """Validate allowed format"""
        validateAllowedFormat(fileName, allowedFormats)

    def validateFileSize(self, f, fileName, minSize, maxSize):
        validateFileSize(f, fileName, minSize, maxSize)

    def _validate(self, value):
        super(FileUpload, self)._validate(value)

        # strip out the path section
        fileName = getCleanFileName(value.filename)

        # validate filename extension
        self.validateFileNameExtension(fileName)

        # validate allowed extension
        self.validateAllowedFormat(fileName, self.allowedFormats)

        # validate file size
        self.validateFileSize(value, fileName, self.minSize, self.maxSize)

