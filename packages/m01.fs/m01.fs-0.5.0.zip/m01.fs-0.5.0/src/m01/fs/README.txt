======
README
======

This package provides a file and storage implementation for zope3 without
using the mongodb GridFS. As you probably know, the GridFS should not get used
for small binar data because it will double the number of queries. This package
will provide a simple file object which stores the file meta and chunk data in
one mongodb document (object).

NOTE: We also provide an m01.grid package which supports th GridFS
implementation with a similar API. The m01.grid is recommended if you need to
store larger data then the mongodb can store for one doucment.


How we process file upload
--------------------------

This description defines how a file upload will get processd in some raw
steps. It defines some internal part we use for processing an input stream
but it doesn't really explain how we implemented the file storage pattern.

The browser defins a form with a file upload input field:

  - client starts file upload

The file upload will get sent to the server:

  - create request

  - read input stream

  - process input stream 

    - define a cgi parser (p01.cgi.parser.parseFormData)

    - parse input stream with cgi parser
    
      - write file upload part in tmp file
  
      - wrap file upload part from input stream with FileUpload
  
    - store FileUpload instance in request.form with the form input field
      name as key

The file upload get processed from the request by using z3c.form components:

  - z3c.form defines a widget

  - z3c.widget reads the FileUpload from the request
  
  - z3c.form data converter returns the plain FileUpload
  
  - z3c.form data manager stores the FileUpload as attribute value

Each file item provides an fileUpload property (attribute) which is responsible
to process the given FileUpload object. The defualt built-in fileUpload
property does the following:

  - get a FileWriter

The FileWrite knows how to write the given FileUpload tmp file to mongodb.


setup
-----

  >>> import re
  >>> from pprint import pprint
  >>> from pymongo import ASCENDING
  >>> import transaction
  >>> import m01.mongo.testing
  >>> import m01.fs.testing

Also define a normalizer:

  >>> patterns = [
  ...    (re.compile("ObjectId\(\'[a-zA-Z0-9]+\'\)"), r"ObjectId('...')"),
  ...    (re.compile("datetime.datetime\([a-zA-Z0-9, ]+tzinfo=<bson.tz_util.FixedOffset[a-zA-Z0-9 ]+>\)"),
  ...                "datetime(..., tzinfo=<bson.tz_util.FixedOffset ...>)"),
  ...    (re.compile("datetime.datetime\([a-zA-Z0-9, ]+tzinfo=[a-zA-Z0-9>]+\)"),
  ...                "datetime(..., tzinfo= ...)"),
  ...    (re.compile("datetime\([a-z0-9, ]+\)"), "datetime(...)"),
  ...    (re.compile("object at 0x[a-zA-Z0-9]+"), "object at ..."),
  ...    ]
  >>> reNormalizer = m01.mongo.testing.RENormalizer(patterns)

Test the file storage:

  >>> db = m01.fs.testing.getTestDatabase()

  >>> files = m01.fs.testing.getTestFilesCollection()
  >>> files.name
  u'test.files'

  >>> storage = m01.fs.testing.SampleFileStorage()
  >>> storage
  <m01.fs.testing.SampleFileStorage object at ...>

Our test setup offers a log handler where we can use like:

  >>> logger.clear()
  >>> print logger


FileStorageItem
---------------

The FileStorageItem is implemented as a IMongoStorageItem and provides IFile.
This item can get stored in a IMongoStorage. This is known as the
container/item pattern. This contrainer only defines an add method which 
implicit uses the items __name__ as key.

  >>> txt = u'Hello World'
  >>> upload = m01.fs.testing.getFileUpload(txt)
  >>> upload.filename
  u'test.txt'
  
  >>> upload.headers
  {}
  
  >>> upload.read()
  'Hello World'
  
  >>> upload.seek(0)
  
  >>> data = {'title': u'title', 'description': u'description'}
  >>> item = m01.fs.testing.SampleFileStorageItem(data)
  >>> firstID = item._id

Apply the file upload item:

  >>> item.applyFileUpload(upload)

And we've got a log entry:

  >>> print logger
  m01.fs DEBUG
    ... ChunkWriter success

  >>> logger.clear()

Try again:

  >>> item.applyFileUpload(upload)
  >>> print logger
  m01.fs DEBUG
    ... ChunkWriter success

  >>> logger.clear()

Now let's see how our FileItem get enhanced with the chunk info:

  >>> reNormalizer.pprint(item.__dict__)
  {'_id': ObjectId('...'),
   '_m_changed': True,
   '_m_initialized': True,
   '_m_parent': None,
   '_pid': None,
   '_type': u'SampleFileStorageItem',
   '_version': 0,
   'contentType': u'text/plain',
   'created': datetime(..., tzinfo= ...),
   'data': Binary('Hello World', 0),
   'description': u'description',
   'filename': u'test.txt',
   'md5': u'b10a8db164e0754105b7a99be72e3fe5',
   'size': 11,
   'title': u'title',
   'uploadDate': datetime(..., tzinfo= ...)}

  >>> reNormalizer.pprint(item.dump())
  {'__name__': u'...',
   '_id': ObjectId('...'),
   '_type': u'SampleFileStorageItem',
   '_version': 0,
   'contentType': u'text/plain',
   'created': datetime(..., tzinfo= ...),
   'data': Binary('Hello World', 0),
   'description': u'description',
   'filename': u'test.txt',
   'md5': u'b10a8db164e0754105b7a99be72e3fe5',
   'removed': False,
   'size': 11,
   'title': u'title',
   'uploadDate': datetime(..., tzinfo= ...)}

Now let's store our item in our storage:

  >>> key = storage.add(item)
  >>> len(key)
  24

  >>> reNormalizer.pprint(item.__dict__)
  {'_id': ObjectId('...'),
   '_m_changed': True,
   '_m_initialized': True,
   '_m_parent': <m01.fs.testing.SampleFileStorage object at ...>,
   '_pid': None,
   '_type': u'SampleFileStorageItem',
   '_version': 0,
   'contentType': u'text/plain',
   'created': datetime(..., tzinfo= ...),
   'data': Binary('Hello World', 0),
   'description': u'description',
   'filename': u'test.txt',
   'md5': u'b10a8db164e0754105b7a99be72e3fe5',
   'size': 11,
   'title': u'title',
   'uploadDate': datetime(..., tzinfo= ...)}

  >>> reNormalizer.pprint(item.dump())
  {'__name__': u'...',
   '_id': ObjectId('...'),
   '_type': u'SampleFileStorageItem',
   '_version': 0,
   'contentType': u'text/plain',
   'created': datetime(..., tzinfo= ...),
   'data': Binary('Hello World', 0),
   'description': u'description',
   'filename': u'test.txt',
   'md5': u'b10a8db164e0754105b7a99be72e3fe5',
   'removed': False,
   'size': 11,
   'title': u'title',
   'uploadDate': datetime(..., tzinfo= ...)}


Now let's commit the items to mongo:

  >>> transaction.commit()

and read the file data:

  >>> item = storage.get(key)
  >>> reader = item.getFileReader()

  >>> reader.read()
  'Hello World'

  >>> reader.seek(0)

  >>> for chunk in reader:
  ...     chunk
  'Hello World'


read
----

Now let's test how we can read files:



update
------

We can also update a file by apply a new fileUpload:

  >>> txt = u'Hello NEW World'
  >>> newUpload = m01.fs.testing.getFileUpload(txt)
  >>> newUpload.filename = u'new.txt'
  >>> newUpload.filename
  u'new.txt'

  >>> item = storage.get(key)
  >>> item.applyFileUpload(newUpload)

As you can see our logger reports that the previous chunk get marked as tmp and 
after upload removed:

  >>> print logger
  m01.fs DEBUG
    ... ChunkWriter success

  >>> logger.clear()

before we commit, let's check if we get a _m_changed marker:

  >>> reNormalizer.pprint(item.__dict__)
  {'_id': ObjectId('...'),
   '_m_changed': True,
   '_m_initialized': True,
   '_m_parent': <m01.fs.testing.SampleFileStorage object at ...>,
   '_pid': None,
   '_type': u'SampleFileStorageItem',
   '_version': 1,
   'contentType': u'text/plain',
   'created': datetime(..., tzinfo=<bson.tz_util.FixedOffset ...>),
   'data': Binary('Hello NEW World', 0),
   'description': u'description',
   'filename': u'new.txt',
   'md5': u'a3875fc03680b88b13b6ea75c49f8abc',
   'modified': datetime(..., tzinfo=<bson.tz_util.FixedOffset ...>),
   'size': 15,
   'title': u'title',
   'uploadDate': datetime(..., tzinfo= ...)}

commit transaction and check the item:

  >>> transaction.commit()

Now let's check the if the storage cache ist empty and we don't get the
cached item without the changed data:

  >>> storage._cache
  {}

Check what we have in mongo:

  >>> files = m01.fs.testing.getTestFilesCollection()
  >>> for data in files.find():
  ...     reNormalizer.pprint(data)
  {u'__name__': u'...',
   u'_id': ObjectId('...'),
   u'_type': u'SampleFileStorageItem',
   u'_version': 2,
   u'contentType': u'text/plain',
   u'created': datetime(..., tzinfo=<bson.tz_util.FixedOffset ...>),
   u'data': Binary('Hello NEW World', 0),
   u'description': u'description',
   u'filename': u'new.txt',
   u'md5': u'a3875fc03680b88b13b6ea75c49f8abc',
   u'modified': datetime(..., tzinfo=<bson.tz_util.FixedOffset ...>),
   u'removed': False,
   u'size': 15,
   u'title': u'title',
   u'uploadDate': datetime(..., tzinfo=<bson.tz_util.FixedOffset ...>)}

And let's load the item with our storage:

  >>> item = storage.get(key)
  >>> reNormalizer.pprint(item.__dict__)
  {'_id': ObjectId('...'),
   '_m_changed': False,
   '_m_initialized': True,
   '_m_parent': <m01.fs.testing.SampleFileStorage object at ...>,
   '_pid': None,
   '_type': u'SampleFileStorageItem',
   '_version': 2,
   'contentType': u'text/plain',
   'created': datetime(..., tzinfo=<bson.tz_util.FixedOffset ...>),
   'data': Binary('Hello NEW World', 0),
   'description': u'description',
   'filename': u'new.txt',
   'md5': u'a3875fc03680b88b13b6ea75c49f8abc',
   'modified': datetime(..., tzinfo=<bson.tz_util.FixedOffset ...>),
   'size': 15,
   'title': u'title',
   'uploadDate': datetime(..., tzinfo=<bson.tz_util.FixedOffset ...>)}

Now let's read the file data:

  >>> reader = item.getFileReader()
  >>> reader.read()
  'Hello NEW World'

  >>> reader.seek(0)

  >>> for chunk in reader:
  ...     chunk
  'Hello NEW World'


FileObject
----------

The FileObject provides IFile and IMongoObject.
