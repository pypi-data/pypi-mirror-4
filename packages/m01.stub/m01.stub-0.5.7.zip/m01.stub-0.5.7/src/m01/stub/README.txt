======
README
======

This package provides a mongo database server testing stub. You can simply
setup such a mongodb stub server in a doctest like::

  import doctest
  import unittest

  from m01.stub import testing

  def test_suite():
      return unittest.TestSuite((
          doctest.DocFileSuite('README.txt',
              setUp=testing.doctestSetUp,
              tearDown=testing.doctestTearDown,
              optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS),
          ))


  if __name__ == '__main__':
      unittest.main(defaultTest='test_suite')

The m01/stub/testing.py module provides a start and stop method which will
download, install, start and stop a mongodb server. All this is done in the
m01/stub/testing/sandbox folder. Everytime a test get started the mongodb/data
folder get removed and a fresh empty database get used.

Note: Also see the zipFolder and unZipFile methods in testing.py which allows
you to setup mongodb data and before remove them store them as a zip file
for a next test run. Such a zipped data folder can get used in another test run
by set the path to the zip file as dataSource argument. Also check the
m01.mongo package for more test use cases.


Testing
-------

Let's use the pymongo package for test our mongodb server stub setup. Note we
use a different port for our stub server setup (45017 instead of 27017):

  >>> from pprint import pprint
  >>> import pymongo
  >>> conn = pymongo.Connection('localhost', 45017)

Let's test our mongodb stub setup:

  >>> pprint(conn.server_info())
  {u'bits': ...,
   u'debug': False,
   u'gitVersion': u'...',
   u'maxBsonObjectSize': ...,
   u'ok': 1.0,
   u'sysInfo': ...,
   u'version': u'2.2.1',
   u'versionArray': [2, 2, 1, 0]}


  >>> conn.database_names()
  [u'local']

setup an index:

  >>> conn.testing.test.collection.ensure_index('dummy')
  u'dummy_1'

add an object:

  >>> _id = conn.testing.test.save({'__name__': u'foo', 'dummy': u'object'})
  >>> _id
  ObjectId('...')

remove them:

  >>> conn.testing.test.remove({'_id': _id})

and check the database names again:

  >>> conn.database_names()
  [u'testing', u'local']

Let's drop the database:

  >>> conn.drop_database("testing")
  >>> conn.database_names()
  [u'local']
