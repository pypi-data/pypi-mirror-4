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
$Id: chunker.py 2918 2012-05-20 02:43:47Z roger.ineichen $
"""
__docformat__ = "reStructuredText"

import datetime
import hashlib
import logging
import math
import os

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

import zope.interface
from zope.contenttype import guess_content_type

from m01.mongo import UTC

import m01.fs.exceptions
from m01.fs import interfaces


logger = logging.getLogger('m01.fs')

_SEEK_SET = os.SEEK_SET
_SEEK_CUR = os.SEEK_CUR
_SEEK_END = os.SEEK_END

BLOCK_SIZE = 16 * 1024 * 1024 # 16 MB


def extractFileName(filename):
    """Stip out path in filename (happens in IE upload)"""
    # strip out the path section even if we do not remove them
    # later, because we just need to check the filename extension.
    cleanFileName = filename.split('\\')[-1]
    cleanFileName = cleanFileName.split('/')[-1]
    dottedParts = cleanFileName.split('.')
    if len(dottedParts) <= 1:
        raise m01.fs.exceptions.MissingFileNameExtension()
    return cleanFileName


def getContentType(filename):
    """Returns the content type based on the given filename"""
    return guess_content_type(filename)[0]


def ChunkIterator(reader):
    while True:
        chunk = reader.read(BLOCK_SIZE)
        if not chunk:
            reader.close()
            raise StopIteration()
        yield chunk
    reader.close()


class ChunkLogging(object):
    """Logging support"""

    def _doLog(self, msg, level=logging.DEBUG):
        logger.log(level, '%s %s %s' % (self._id, self.__class__.__name__, msg))

    def info(self, msg):
        self._doLog(msg, logging.INFO)

    def debug(self, msg):
        self._doLog(msg, logging.DEBUG)

    def error(self, msg):
        self._doLog(msg, logging.ERROR)

    
class ChunkWriterBase(ChunkLogging):
    """File chunk writer base class"""

    zope.interface.implements(interfaces.IChunkWriter)

    def __init__(self):
        """Setup ChunkWriterBase basics"""
        self._closed = False

    @property
    def closed(self):
        """Return close marker"""
        return self._closed

    def close(self):
        """Mark the file as closed

        A closed file cannot be written any more. Calling `close` more than
        once is allowed.
        """
        if not self._closed:
            self._closed = True

    def validate(self, fileUpload):
        """Validate file upload item"""
        if self._closed:
            raise ValueError("cannot write to a closed file")
        elif not fileUpload or not fileUpload.filename:
            # empty string or None or missing filename means no upload given
            raise ValueError("Missing file upload data")
        elif self.removed:
            raise ValueError("Can't store data for removed files")

    def setFileName(self, filename):
        """Set filename (hook for adjust the given filename)"""
        self.context.filename = unicode(filename)

    def setContentType(self, contentType):
        """Set content type (hook for adjust the given type)"""
        self.context.contentType = unicode(contentType)

    def write(self, data):
        """Write data to IFile context"""
        if self._closed:
            raise ValueError("cannot write to a closed file")
        try:
            # file-like
            read = data.read
        except AttributeError:
            # string
            if not isinstance(data, basestring):
                raise TypeError("can only write strings or file-like objects")
            if isinstance(data, unicode):
                try:
                    data = data.encode(self.encoding)
                except AttributeError:
                    raise TypeError("must specify an encoding for file in "
                                    "order to write unicode")
            read = StringIO(data).read

        # write data to context
        data = read()
        # calculate and set md5
        digester = hashlib.md5()
        digester.update(data)
        self.size = len(data)
        self.context.data = data
        return digester

    def addData(self, data, filename, contentType):
        """Add file like item or string data as chunk"""
        success = False
        try:
            # make sure we begin at the start
            digester = self.write(data)
            md5 = digester.hexdigest()
            # marker for successfully added chunk
            success = True
        except Exception, e:
            self.error('add caused an error')
            # and raise the exception
            raise e
        if success:
            # apply metadata to adapted IFile
            self.setFileName(filename)
            self.setContentType(contentType)
            self.context.md5 = unicode(md5)
            self.context.size = self.size
            self.context.uploadDate = datetime.datetime.now(UTC)
            self.debug('success')

    def add(self, fileUpload):
        """Add file upload item as chunk"""
        success = False
        self.validate(fileUpload)
        filename = extractFileName(fileUpload.filename)
        contentType = getContentType(filename)
        try:
            # make sure we begin at the start
            fileUpload.seek(0)
            digester = self.write(fileUpload)
            md5 = digester.hexdigest()
            # marker for successfully added chunk
            success = True
        except Exception, e:
            self.error('add caused an error')
            # and raise the exception
            raise e
        finally:
            self.close()
        if success:
            # apply metadata to adapted IFile
            self.setFileName(filename)
            self.setContentType(contentType)
            self.context.md5 = unicode(md5)
            self.context.size = self.size
            self.context.uploadDate = datetime.datetime.now(UTC)
            self.debug('success')

    def __enter__(self):
        """Support for the context manager protocol"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Support for the context manager protocol.

        Close the file and allow exceptions to propogate.
        """
        self.close()
        # propogate exceptions
        return False


class ChunkWriter(ChunkWriterBase):
    """File chunk writer adapter"""

    zope.component.adapts(interfaces.IFile)

    def __init__(self, context):
        """Setup ChunkWriter based on adapted IFile context"""
        super(ChunkWriter, self).__init__()
        self.context = context
        self._id = context._id
        if not self._id:
            raise ValueError("Missing mongo ObjectId", self._id)
        self.removed = self.context.removed


class ChunkReaderBase(ChunkLogging):
    """File chunk reader adapter"""


    zope.interface.implements(interfaces.IChunkReader)

    def __init__(self):
        self._buffer = ""
        self._position = 0
        self._closed = False

    @property
    def __name__(self):
        """simply map filename as __name__ (common in zope)"""
        return self.context.filename

    def validate(self):
        if self.removed:
            raise ValueError("Can't read data from removed files")

    def close(self):
        """Support file-like API"""
        pass

    def read(self, size=-1):
        """Read at most `size` bytes from the file data

        If size is negative or omitted all data get returned
        """
        # validate read operation
        self.validate()

        res = ""

        if size == 0:
            res = ""
        elif size < 0:
            # set position at the end of our data
            self._position = int(self.size)
            # return all data
            res = self.context.data
        elif self._position == 0 and size > int(self.size):
            # set position at the end of our data
            self._position = int(self.size)
            # return all data
            res = self.context.data
        else:
            # get current position
            position = self._position
            # calculate pending data size
            pending = int(self.size) - position
            if size < pending:
                # return oly partial data based on position and size
                self._position = position + size
                res = self.context.data[position:end]
            else:
                # set position at the end out our data
                self._position = position + pending
                # return less then asked for because thre is not more data
                res = self.context.data[position:]

        # return a string and not the Binary instance
        return str(res)

    def readline(self, size=-1):
        """Read one line or up to `size` bytes from the file data"""
        bytes = ""
        while len(bytes) != size:
            byte = self.read(1)
            bytes += byte
            if byte == "" or byte == "\n":
                break
        return bytes

    def tell(self):
        """Return the current position of this file"""
        return self._position

    def seek(self, pos, whence=_SEEK_SET):
        """Set the current position of this file"""
        if whence == _SEEK_SET:
            new_pos = pos
        elif whence == _SEEK_CUR:
            new_pos = self._position + pos
        elif whence == _SEEK_END:
            new_pos = int(self.size) + pos
        else:
            raise IOError(22, "Invalid value for `whence`")
        if new_pos < 0:
            raise IOError(22, "Invalid value for `pos` - must be positive")
        self._position = new_pos
        self._buffer = ""

    def __iter__(self):
        """Return an iterator over all of this file's data"""
        # validate read operation
        self.validate()
        # return iterator
        return ChunkIterator(self)

    def __enter__(self):
        """Makes it possible to use with the context manager protocol"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Makes it possible to use with the context manager protocol"""
        return False


class ChunkReader(ChunkReaderBase):
    """File chunk reader adapter"""

    zope.component.adapts(interfaces.IFile)

    def __init__(self, context):
        """Setup chunk reader based on adapted context"""
        super(ChunkReader, self).__init__()
        self.context = context
        self._id = context._id
        if not self._id:
            raise ValueError("Missing mongo ObjectId", self._id)
        self.size = self.context.size
        self.md5 = self.context.md5
        self.filename = self.context.filename
        self.contentType = self.context.contentType
        self.uploadDate = self.context.uploadDate
        self.removed = self.context.removed


class ChunkDataReader(ChunkReaderBase):
    """Chunk data reader based on given mongodb file data"""

    def __init__(self, data):
        """Setup chunk reader based on given file data"""
        super(ChunkDataReader, self).__init__()
        self._id = data['_id']
        if not self._id:
            raise ValueError("Missing mongo ObjectId", self._id)
        self.size = data['size']
        self.md5 = data['md5']
        self.filename = data['filename']
        self.contentType = data['contentType']
        self.uploadDate = data['uploadDate']
        self.removed = data['removed']


def getChunkDataReader(collection, query):
    """Lookup a file and return a ChunkDataReader"""
    # get data
    data = collection.find_one(query)
    return ChunkDataReader(data)
