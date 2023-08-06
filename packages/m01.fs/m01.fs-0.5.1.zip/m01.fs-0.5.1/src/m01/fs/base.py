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
$Id: base.py 3666 2013-03-17 17:30:44Z roger.ineichen $
"""
__docformat__ = "reStructuredText"

import m01.mongo.base
from m01.mongo.fieldproperty import MongoFieldProperty
from m01.mongo.fieldproperty import MongoBinaryProperty

from m01.fs import interfaces
import m01.fs.chunker


class FileBase(object):
    """File base class"""

    data = MongoBinaryProperty(interfaces.IFile['data'])

    size = MongoFieldProperty(interfaces.IFile['size'])
    md5 = MongoFieldProperty(interfaces.IFile['md5'])
    filename = MongoFieldProperty(interfaces.IFile['filename'])
    contentType = MongoFieldProperty(interfaces.IFile['contentType'])
    uploadDate = MongoFieldProperty(interfaces.IFile['uploadDate'])

    removed = MongoFieldProperty(interfaces.IFile['removed'])

    @property
    def collection(self):
        """Returns a mongodb collection for store file meta and chunks data."""
        raise NotImplementedError(
            "Subclass must implement the collection attribute")

    def getFileWriter(self):
        """Returns a IChunkReader"""
        return m01.fs.chunker.ChunkWriter(self)

    def getFileReader(self):
        """Returns a IChunkReader"""
        return m01.fs.chunker.ChunkReader(self)

    def applyFileUpload(self, fileUpload):
        """Apply FileUpload given from request publisher"""
        if not fileUpload or not fileUpload.filename:
            # empty string or None means no upload
            raise ValueError("Missing file upload data")
        elif self.removed:
            raise ValueError("Can't store data for removed files")
        writer = self.getFileWriter()
        writer.add(fileUpload)

    def __repr__(self):
        return "<%s %r>" % (self.__class__.__name__, self.__name__)


class FileItemBase(FileBase, m01.mongo.base.MongoItemBase):
    """Mongo file item base class."""

    _dumpNames = ['_id', '_pid', '_type', '_version', '__name__',
                  'created', 'modified', 'removed',
                  'data', 'size', 'md5', 'filename', 'contentType',
                  'uploadDate',]


class SecureFileItemBase(FileBase, m01.mongo.base.SecureMongoItemBase):
    """Secure mongo file item base class."""

    _dumpNames = ['_id', '_pid', '_type', '_version', '__name__',
                  'created', 'modified', 'removed',
                  '_ppmrow', '_ppmcol',
                  '_prmrow', '_prmcol',
                  '_rpmrow', '_rpmcol',
                  'data', 'size', 'md5', 'filename', 'contentType',
                  'uploadDate',]
