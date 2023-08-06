This package provides a mongodb file implementation without GridFS for Zope3.
This means, such files are limited to the mongo document size, currently 16MB.
As you probably know, you should not use GridFS for small binary data because
you will double the number of queries. This package will offer a file which
stores the meta and file data in one document. 
