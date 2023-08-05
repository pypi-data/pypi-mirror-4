======
README
======

This package provides a setup and teardown concept for WSGI server applications
and a test headless WebKit browser. This is usefull for real application tests
using a real browser. Otherwise there is only selenium, windmill or other fancy
stuff you can use for testing. Mechanize and other mechanize based zope
testbrowser can not execute javascript.

  >>> from p01.tester.browser import WebKitBrowser


Testing
-------

This test uses a realistic setup like you will us in your application tests.
Let's setup a WSGIBrowser and start accessing our server:

  >>> appURL = 'http://localhost:9090/'
  >>> browser = WebKitBrowser()
  >>> browser.open(appURL + 'test.html')

  >>> browser.url
  u'http://localhost:9090/test.html'

  >>> print browser.html
  <html><head></head><body>Test Response</body></html>

Let's setup a second browser before we close the first one:

  >>> browser2 = WebKitBrowser()
  >>> browser2.open(appURL + 'hello.html')
  >>> browser2.url
  u'http://localhost:9090/hello.html'

Now close them:

  >>> browser.close()

  >>> browser2.close()

As you can see, our browser is no available anymore. Another call after close
a browser will end with a RuntimeError:

  >>> browser.open(appURL + 'test.html')
  Traceback (most recent call last):
  ...
  UsageError: WebKitBrowser was closed, you need to setup another one

Close a browser twice will not raise any error:

  browser.close()
