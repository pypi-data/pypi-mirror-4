###############################################################################
#
# Copyright (c) 2011 Projekt01 GmbH and Contributors.
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
$Id: __init__.py 2795 2012-03-03 17:54:07Z roger.ineichen $
"""
__docformat__ = "reStructuredText"

import os
import tempfile

import zope.schema
from zope.publisher.browser import FileUpload
from zope.testing.loggingsupport import InstalledHandler

import m01.mongo.interfaces
import  m01.mongo.pool
import m01.mongo.testing
import m01.stub.testing
from m01.mongo.fieldproperty import MongoFieldProperty

from m01.fs import interfaces
import m01.fs.item

TEST_DB_NAME = 'm01_fs_testing'


##############################################################################
#
# test setup methods
#
##############################################################################

_testConnection = None

def getTestConnection():
    global _testConnection
    return _testConnection

def getTestDatabase():
    global _testConnection
    return _testConnection[TEST_DB_NAME]

def dropTestDatabase():
    if _testConnection is not None:
        _testConnection.drop_database(TEST_DB_NAME)

def getTestFilesCollection():
    db = getTestDatabase()
    return db.test.files


# stub mongodb server
def setUpMongoDBHook():
    def getMongoDBStubSetUp(test):
        # lazy test setup
        host = 'localhost'
        port = 45030
        here = os.path.dirname(__file__)
        sandBoxDir = os.path.join(here, 'sandbox')
        m01.stub.testing.startMongoDBServer(host, port, sandBoxDir=sandBoxDir)
        p = m01.mongo.pool.MongoConnectionPool(host, port)
        global _testConnection
        _testConnection = p.connection
        logger = InstalledHandler('m01.fs')
        test.globs['logger'] = logger
    return getMongoDBStubSetUp

setUpMongoDB = setUpMongoDBHook()

def tearDownMongoDBHook():
    def getMongoDBStubTearDown(test):
        # lazy test tear down
        m01.stub.testing.stopMongoDBServer()
        _testConnection = None
        logger = test.globs['logger']
        logger.clear()
        logger.uninstall()
    return getMongoDBStubTearDown

tearDownMongoDB = tearDownMongoDBHook()


###############################################################################
#
# test helper
#
###############################################################################

class FakeFieldStorage(object):
    """A fake field storage"""

    def __init__(self, upload, filename, headers):
        self.file = upload
        self.filename = filename
        self.headers = headers

def getFileUpload(txt, filename=None, headers=None):
    if filename is None:
        filename = 'test.txt'
    if headers is None:
        headers = {}
    upload = tempfile.SpooledTemporaryFile('w+b')
    upload.write(txt)
    upload.seek(0)
    fieldStorage = FakeFieldStorage(upload, filename, headers)
    return FileUpload(fieldStorage)


###############################################################################
#
# Public Base Tests
#
###############################################################################

class FileItemBaseTest(m01.mongo.testing.MongoItemBaseTest):
    """fileItem base test"""

    def test_providedBy_IFile(self):
        obj = self.makeTestObject()
        self.assert_(interfaces.IFile.providedBy(obj), True)

    def test_providedBy_IFileItem(self):
        obj = self.makeTestObject()
        self.assert_(interfaces.IFileItem.providedBy(obj), True)


class FileObjectBaseTest(m01.mongo.testing.MongoObjectBaseTest):
    """fileItem base test"""

    def test_providedBy_IFile(self):
        obj = self.makeTestObject()
        self.assert_(interfaces.IFile.providedBy(obj), True)

    def test_providedBy_IFileObject(self):
        obj = self.makeTestObject()
        self.assert_(interfaces.IFileObject.providedBy(obj), True)


###############################################################################
#
# test components
#
###############################################################################

class TestFilesCollectionMixin(object):
    """Test files collection mixin class"""

    @property
    def collection(self):
        return getTestFilesCollection()


class ITestSchema(zope.interface.Interface):
    """Basic test schema."""

    title = zope.schema.TextLine(
        title=u'Title',
        description=u'Title',
        default=u'',
        required=True)

    description = zope.schema.Text(
        title=u'Description',
        description=u'Description',
        default=u'',
        required=False)


class ISampleFileStorageItem(ITestSchema, interfaces.IFileStorageItem):
    """Sample storage file item interface."""

    __name__ = zope.schema.TextLine(
        title=u'Title',
        description=u'Title',
        missing_value=u'',
        default=None,
        required=True)


class SampleFileStorageItem( m01.fs.item.FileStorageItem):
    """Sample file storage item."""

    zope.interface.implements(ISampleFileStorageItem)

    title = MongoFieldProperty(ISampleFileStorageItem['title'])
    description = MongoFieldProperty(ISampleFileStorageItem['description'])

    dumpNames = ['title', 'description']


class ISampleFileStorage(m01.mongo.interfaces.IMongoStorage):
    """Sample file storage interface."""


class SampleFileStorage(TestFilesCollectionMixin,
    m01.mongo.storage.MongoStorage):
    """Sample file storage."""

    zope.interface.implements(ISampleFileStorage)

    def __init__(self):
        pass

    def load(self, data):
        """Load data into the right mongo item."""
        return SampleFileStorageItem(data)
