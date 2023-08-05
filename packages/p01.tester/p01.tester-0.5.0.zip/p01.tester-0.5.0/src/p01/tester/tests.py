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
$Id: tests.py 3131 2012-09-29 20:08:46Z roger.ineichen $
"""
__docformat__ = "reStructuredText"

import os
import os.path
import time
import doctest
import unittest

import p01.tester.server
import p01.tester.testing


JQUERY_VERSION = '1.8.1'
JQUERY_SIMULATE_VERSION = 'r6063'

JQUERY_FILENAME = 'jquery-%s.js' % JQUERY_VERSION
JQUERY_SIMULATE_FILENAME = 'jquery.simulate-%s.js' % JQUERY_SIMULATE_VERSION

JQUERY_URL = 'http://localhost:9090/%s' % JQUERY_FILENAME


HERE = os.path.dirname(__file__)
SOURCE = os.path.join(HERE, 'source')
JQUERY = os.path.join(SOURCE, JQUERY_FILENAME)
SIMULATE = os.path.join(SOURCE, JQUERY_SIMULATE_FILENAME)
POST = os.path.join(SOURCE, 'post.js')


# test application
SEARCH_HTML = """<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml"> 
<head>
  <script type="text/javascript" src="%(jQueryURL)s"></script>
  <script type="text/javascript">
    var state = null;
    jQuery(document).ready(function ($) {
      state = 'ready';
      $('#form-widgets-text').val('search something');
      $('#form-widgets-submit').click(function() {
        $('#form').submit();
      });
    });
  </script>
</head>
<body>
  <form action="./search.html" method="POST" id="form">
    <input type="text"
           id="form-widgets-text"
           name="form.widgets.text" value="" />
    <input type="button"
           id="form-widgets-submit"
           value="submit me" />
    %(result)s
  </form>
</body>
</html>
"""

SEARCH_RESULT = """
<div id="result">
  <strong>Result</strong>
  <div class="item">here comes your search result</div>
</div>
"""

POST_HTML = """<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml"> 
<head>
  <script type="text/javascript" src="%(jQueryURL)s"></script>
  <script type="text/javascript">
    var state = null;
    jQuery(document).ready(function ($) {
      // load asap
      $.ajax({
        url: "http://localhost:9090/post-first.html",
        type: 'POST',
        dataType: 'json',
        processData: false,
        async: false,
        success: function(data, textStatus) {
          $('#result').html(data.result);
          $('#status').html(textStatus);
        },
        error: function(jqXHR, textStatus, errorThrown) {
          $('#result').html("FIRST ERROR");
          $('#status').html(textStatus);
        }
      });
      // clickable json loader
      $('#clickable').click(function() {
        $.ajax({
          url: "http://localhost:9090/post-second.html",
          type: 'POST',
          dataType: 'json',
          processData: false,
          async: false,
          success: function(data, textStatus) {
            $('#result').html(data.result);
            $('#status').html(textStatus);
          },
          error: function(jqXHR, textStatus, errorThrown) {
            $('#result').html("SECOND ERROR");
            $('#status').html(textStatus);
          }
        });
      });
    });
  </script>
</head>
<body>
  <form action="http://localhost:9090/post-nada.html" method="POST" id="form">
    <input type="button"
           id="clickable"
           value="clickable" />
    <div id="result">nada</div>
    <div id="status">nada</div>
  </form>
</body>
</html>
"""
POST_FIRST = '{"id":"jsonid", "result": "FIRST DATA", "error":""}'
POST_SECOND = '{"id":"jsonid", "result": "SECOND DATA", "error":""}'


class WSGITestApplication(object):
    """WSGI test application"""

    def __init__(self):
        self.counts = {}

    def __call__(self, environ, start_response):
        """Simple test application which can handle some urls"""
        path = environ['PATH_INFO']
        count = self.counts.setdefault(path, 0)
        self.counts[path] += 1

        # take care that we are not server pages to fast. At least the
        # ajax search.html call will fail if we don't use a timeout
        time.sleep(0.1)

        # browser.txt test data
        if path.endswith('test.html'):
            start_response('200 Ok', [('Content-Type', 'text/html'),])
            return ['<html>Test Response</html>']
        elif path.endswith('hello.html'):
            q = environ.get('QUERY_STRING')
            if q:
                name = q.split('=')[1]
            else:
                name = 'not defined'
            start_response('200 Ok', [('Content-Type', 'text/html'),])
            return ['<html>Hello %s</html>' % name]
        elif path.endswith('counter.html'):
            start_response('200 Ok', [('Content-Type', 'text/html'),])
            return ['<html><p>Call %d, path %s</p></html>' % (count, path)]
        elif path.endswith('search.html'):
            if environ['CONTENT_TYPE'] == 'application/x-www-form-urlencoded':
                # this is a search form submit request
                result = SEARCH_RESULT
                contentType = 'application/xhtml+xml'
            else:
                result = '<!-- no result given -->'
                contentType = 'text/html'
            data = {'jQueryURL': JQUERY_URL,
                    'result': result}
            start_response('200 Ok', [('Content-Type', contentType),])
            return [SEARCH_HTML % data]

        # ajax.txt test data
        elif path.endswith('post.html'):
            data = {'jQueryURL': JQUERY_URL}
            start_response('200 Ok', [('Content-Type', 'text/html'),])
            return [POST_HTML % data]
        elif path.endswith('post-first.html'):
            start_response('200 Ok', [('Content-Type', 'application/json'),])
            return [POST_FIRST]
        elif path.endswith('post-second.html'):
            start_response('200 Ok', [('Content-Type', 'application/json'),])
            return [POST_SECOND]

        # js scripts
        elif path.endswith(JQUERY_FILENAME):
            res = open(JQUERY).read()
            start_response('200 Ok', [
                ('Content-Type', 'application/javascript'),
                ('Content-Length', str(len(res)))
            ])
            return [res]
        elif path.endswith(JQUERY_SIMULATE_FILENAME):
            res = open(SIMULATE).read()
            start_response('200 Ok', [
                ('Content-Type', 'application/javascript'),
                ('Content-Length', str(len(res)))
            ])
            return [res]
#        elif path.endswith('post.js'):
#            res = open(POST).read()
#            start_response('200 Ok', [
#                ('Content-Type', 'application/javascript'),
#                ('Content-Length', str(len(res)))
#            ])
#            return [res]
        else:
            start_response('404 Not Found', [
                ('Content-Type', 'application/xhtml+xml'),])
            return ['<div>Not Found</div>']


def setUpWSGITestApplication(test=None):
    app_factory = WSGITestApplication()
    # start a test WSGI server with our application
    p01.tester.server.startWSGIServer('testing', app_factory)
    # setup QApplication
    p01.tester.testing.setUpQApplication()


def tearDownWSGITestApplication(test=None):
    # stop the test WSGI server serving our application
    p01.tester.server.stopWSGIServer('testing')
    # tear down QApplication
    p01.tester.testing.tearDownQApplication()


def test_suite():
    return unittest.TestSuite((
        doctest.DocFileSuite('README.txt',
            setUp=setUpWSGITestApplication,
            tearDown=tearDownWSGITestApplication,
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS),
        doctest.DocFileSuite('browser.txt',
            setUp=setUpWSGITestApplication,
            tearDown=tearDownWSGITestApplication,
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS),

        doctest.DocFileSuite('ajax.txt',
            setUp=setUpWSGITestApplication,
            tearDown=tearDownWSGITestApplication,
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS),
        # running twice was raising an error based on bad xmlhtp reply handling
        # in PySide 1.1.1 and PyQt based on Qt 4.7
        doctest.DocFileSuite('ajax.txt',
            setUp=setUpWSGITestApplication,
            tearDown=tearDownWSGITestApplication,
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS),

        doctest.DocFileSuite('server.txt',
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS),
        doctest.DocFileSuite('xpath.txt',
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS),

        ))


if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
