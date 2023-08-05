======
README
======

setup
-----

This test is using an elasticsearch server. The test setUp method used for this
test is calling our startElasticSearchServer method which is starting an
elasticsearch server. The first time a test get called a new elasticsearch
server will get downloaded (by default version 0.19.2). The test setup looks
like::

  def test_suite():
      return unittest.TestSuite((
          doctest.DocFileSuite('README.txt',
              setUp=testing.doctestSetUp, tearDown=testing.doctestTearDown,
              optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
              encoding='utf-8'),
          ))

If you like to set some custom settings, you can use the confSource which must
point to a config folder with elasticsearch.yml, logging.yml and optinal
mapping definitions. Your custom doctest setUp and tearDown method could look
like::

  def mySetUp(test):
      # use default elasticsearch with our server and conf source dir
      here = os.path.dirname(__file__)
      serverDir = os.path.join(here, 'server')
      confSource = os.path.join(here, 'config')
      p01.elasticstub.testing.startElasticSearchServer(serverDir=serverDir,
          confSource=confSource)

  def myTearDown(test):
      p01.elasticstub.testing.stopElasticSearchServer()
      # do some custom teardown stuff here


testing
-------

First import simplejson as json and define a method which helps to convert
differences in json and simplejson in different python versions:

  >>> import simplejson
  >>> def jsonLoads(jsonStr):
  ...     return simplejson.loads(unicode(jsonStr))

Let's setup a python httplib connection:

  >>> import httplib
  >>> conn = httplib.HTTPConnection('localhost', 45200)

and test the cluster state:

  >>> conn.request('GET', '_cluster/state')
  >>> response = conn.getresponse()
  >>> response.status
  200

  >>> from pprint import pprint
  >>> body = response.read()
  >>> pprint(jsonLoads(body))
  {u'allocations': [],
   u'blocks': {},
   u'cluster_name': u'p01_elasticstub_testing',
   u'master_node': u'...',
   u'metadata': {u'indices': {}, u'templates': {}},
   u'nodes': {u'...': {u'attributes': {},
                                          u'name': u...,
                                          u'transport_address': u'inet[...]'}},
   u'routing_nodes': {u'nodes': {}, u'unassigned': []},
   u'routing_table': {u'indices': {}}}

As you can see our mapping is empty:

  >>> conn.request('GET', '/testing/test/_mapping')
  >>> response = conn.getresponse()
  >>> body = response.read()
  >>> pprint(jsonLoads(body))
  {u'error': u'IndexMissingException[[testing] missing]', u'status': 404}

Let's index a simple item:

  >>> body = simplejson.dumps({u'title': u'Title'})
  >>> conn.request('POST', '/testing/test/1', body)
  >>> response = conn.getresponse()
  >>> body = response.read()
  >>> pprint(jsonLoads(body))
  {u'_id': u'1',
   u'_index': u'testing',
   u'_type': u'test',
   u'_version': 1,
   u'ok': True}

refresh:

  >>> conn.request('GET', '/testing/test/_refresh')
  >>> response = conn.getresponse()
  >>> body = response.read()
  >>> pprint(jsonLoads(body))
  {u'_id': u'_refresh',
   u'_index': u'testing',
   u'_type': u'test',
   u'exists': False}

and test our mapping again:

  >>> conn.request('GET', '/testing/test/_mapping')
  >>> response = conn.getresponse()
  >>> body = response.read()
  >>> pprint(jsonLoads(body))
  {u'test': {u'properties': {u'title': {u'type': u'string'}}}}
