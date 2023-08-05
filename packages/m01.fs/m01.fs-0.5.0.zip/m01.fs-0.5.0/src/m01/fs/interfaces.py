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
$Id: interfaces.py 3048 2012-09-02 05:33:38Z roger.ineichen $
"""
__docformat__ = "reStructuredText"

import os
import zope.schema
import zope.i18nmessageid
from zope.publisher.interfaces.http import IResult

import z3c.form.interfaces

import m01.mongo.interfaces
import m01.mongo.schema

import m01.fs.schema

_ = zope.i18nmessageid.MessageFactory('p01')


_SEEK_SET = os.SEEK_SET


# widget
class IFileUploadWidget(z3c.form.interfaces.IFileWidget):
    """Widget for IFileUpload field.

    The FileUploadDataConverter for this widget returns the plain
    FileUpload which wraps the tmp file.
    
    see: zope.publisher.browser.FileUpload
    """


# upload widget schema (ignoreContext=True)
class IFileUploadSchema(zope.interface.Interface):
    """Schema for render a FileUpload widget"""

    # used in z3c.form for render a IFileUploadWidget with ignoreContext=True
    fileUpload = m01.fs.schema.FileUpload(
        title=_(u'File Upload'),
        description=_(u'File Upload'),
        default=None,
        required=True)


# IFile
class IFileSchema(zope.interface.Interface):
    """File schema without method definition.
    
    Note: This interface is used for IFile and IChunkReader
    """

    data = m01.mongo.schema.MongoBinary(
        title=u'File data',
        description=u'File data',
        required=True)

    filename = zope.schema.TextLine(
        title=_(u'Filename'),
        description=_(u'Filename'),
        required=True)

    contentType = zope.schema.TextLine(
        title=_(u'Content Type'),
        description=_(u'Content Type'),
        required=True)

    size = zope.schema.Int(
        title=_(u'File size'),
        description=_(u'File size'),
        default=0,
        required=True)

    md5 = zope.schema.TextLine(
        title=_(u'MD5'),
        description=_(u'MD5'),
        default=None,
        required=True)

    uploadDate = zope.schema.Datetime(
        title=_(u'Upload date'),
        description=_(u'Upload date'),
        default=None,
        required=True)

    removed = zope.schema.Bool(
        title=u'removed marker',
        description=u'removed marker',
        default=False,
        required=True)


class IFile(IFileSchema):
    """File without ILocation.
    
    Note: This interface doens't provide ILocation or IContained. The missing
    ILocation interface in this interface makes it simpler for define correct
    permissions in ZCML.
    """

    def getFileWriter():
        """Returns a IChunkReader"""

    def getFileReader():
        """Returns a IChunkReader"""

    def applyFileUpload(fileUpload):
        """Apply FileUpload given from request publisher"""


class IFileItem(IFile, m01.mongo.interfaces.IMongoItem):
    """Mongo file providing IMongoItem""" 


# IFileItem
class IFileStorageItem(IFileItem, m01.mongo.interfaces.IMongoStorageItem):
    """IMongoStorageItem providing IFile."""


class ISecureFileStorageItem(IFileItem,
    m01.mongo.interfaces.ISecureMongoStorageItem):
    """ISecureMongoStorageItem providing IFile."""


class IFileContainerItem(IFileItem, m01.mongo.interfaces.IMongoContainerItem):
    """IMongoContainerItem providing IFile."""


class ISecureFileContainerItem(IFileItem,
    m01.mongo.interfaces.ISecureMongoContainerItem):
    """ISecureMongoContainerItem providing IFile."""


# IFileObject
class IFileObject(IFileItem, m01.mongo.interfaces.IMongoObject):
    """IMongoObject providing IFile."""


# chunk helper
class IChunkIterator(zope.interface.Interface):
    """Chunk iterator"""

    def __iter__(self):
        """iter"""

    def next(self):
        """next"""

class IChunkWriter(zope.interface.Interface):
    """Grid data writer for IFile"""

    closed = zope.schema.Bool(
        title=u'close marker',
        description=u'close marker',
        default=False,
        readonly=True,
        required=True)

    def close():
        """Close an open file handle."""

    def write(data):
        """Write data to mongodb"""

    def add(fileUpload):
        """Add file upload data as chunk"""

    def remove():
        """Mark chunk data as removed"""

    def __enter__():
        """Support for the context manager protocol"""

    def __exit__(exc_type, exc_val, exc_tb):
        """Support for the context manager protocol.

        Close the file and allow exceptions to propogate.
        """


class IChunkReader(IResult, IFileSchema):
    """Chunk data reader for IFile also providing IResult
    
    A ChunkReader also provides IFileSchema attribute access to the adapted
    context

    """

    def read(size=-1):
        """Read at most `size` bytes from the file

        If size is negative or omitted all data is read
        """

    def readline(size=-1):
        """Read one line or up to `size` bytes from the file"""

    def tell():
        """Return the current position of this file"""

    def seek(pos, whence=_SEEK_SET):
        """Set the current position of this file"""

    def __iter__():
        """Return an iterator over all of this file's data"""

    def close():
        """Support file-like API"""

    def __enter__():
        """Makes it possible to use with the context manager protocol"""

    def __exit__(exc_type, exc_val, exc_tb):
        """Makes it possible to use with the context manager protocol"""

