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
$Id: item.py 2798 2012-03-04 02:29:53Z roger.ineichen $
"""
__docformat__ = "reStructuredText"

import zope.interface
import zope.location.interfaces

import m01.mongo.interfaces
from m01.mongo import LOCAL
from m01.mongo.fieldproperty import MongoFieldProperty

import m01.fs.base
from m01.fs import interfaces


class FileStorageItem(m01.fs.base.FileItemBase):
    """Simple mongo file item.
    
    This FileStorageItem will use the mongo ObjectId as the __name__. This
    means you can't set an own __name__ value for this object.

    Implement your own IFileStorageItem with the attributes you need and the
    relevant chunks collection.
    """

    zope.interface.implements(interfaces.IFileStorageItem,
        m01.mongo.interfaces.IMongoParentAware,
        zope.location.interfaces.ILocation)

    _skipNames = ['__name__']

    @property
    def __name__(self):
        return unicode(self._id)


class SecureFileStorageItem(m01.fs.base.SecureFileItemBase):
    """Security aware IFileStorageItem."""

    zope.interface.implements(interfaces.ISecureFileStorageItem,
        m01.mongo.interfaces.IMongoParentAware,
        zope.location.interfaces.ILocation)

    _skipNames = ['__name__']

    @property
    def __name__(self):
        return unicode(self._id)


class FileContainerItem(m01.fs.base.FileItemBase):
    """File container item.

    Implement your own IFileContainerItem with the attributes you need and the
    relevant chunks collection.
    """

    zope.interface.implements(interfaces.IFileStorageItem,
        m01.mongo.interfaces.IMongoParentAware,
        zope.location.interfaces.ILocation)

    _skipNames = []

    # validate __name__ and observe to set _m_changed
    __name__ = MongoFieldProperty(
        zope.location.interfaces.ILocation['__name__'])


class SecureFileContainerItem(m01.fs.base.SecureFileItemBase):
    """Security aware IFileStorageItem."""

    zope.interface.implements(interfaces.ISecureFileContainerItem,
        m01.mongo.interfaces.IMongoParentAware,
        zope.location.interfaces.ILocation)

    # validate __name__ and observe to set _m_changed
    __name__ = MongoFieldProperty(
        zope.location.interfaces.ILocation['__name__'])


class FileObject(m01.fs.base.FileBase, m01.mongo.item.MongoObject):
    """MongoObject based file"""

    zope.interface.implements(interfaces.IFileObject)

    _dumpNames = ['_id', '_oid', '__name__', '_type', '_version',
                  '_field',
                  'created', 'modified', 'removed',
                  'data', 'size', 'md5', 'filename', 'contentType',
                  'uploadDate']

    @property
    def collection(self):
        return self.getCollection(self.__parent__)

    def getFileWriter(self):
        return m01.fs.chunker.ChunkWriter(self)

    def getFileReader(self):
        return m01.fs.chunker.ChunkReader(self)
