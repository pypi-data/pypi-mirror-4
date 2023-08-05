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
$Id: browser.py 3131 2012-09-29 20:08:46Z roger.ineichen $
"""
__docformat__ = "reStructuredText"

from cStringIO import StringIO
import formatter
import htmllib
import logging
import os
import re
import time
import sys
import urlparse
from pprint import pprint

import lxml.etree
import lxml.html

import pkg_resources

import qt_compat
QtCore = qt_compat.QtCore
QtGui = qt_compat.import_module("QtGui")
QtNetwork = qt_compat.import_module("QtNetwork")
QtWebKit = qt_compat.import_module("QtWebKit")

import p01.tester.exceptions
import p01.tester.xpath

import p01.tester.testing

logger = logging.getLogger('p01.tester')

RE_CHARSET = re.compile('.*;charset=(.*)')


# Debug levels
CRITICAL = logging.CRITICAL
ERROR = logging.ERROR
WARNING = logging.WARNING
INFO = logging.INFO
DEBUG = logging.DEBUG
NOTSET = logging.NOTSET

jQueryFileName = 'jquery-1.8.1.js'
jQuerySimulateFileName = 'jquery.simulate-r6063.js'

# helper
def escape(value):
    """Prevent jquery calls like self.jq('jq('#foo')')"""
    return  value.replace("'", "\\'")

# cookie support
def toString(value):
    """Convert to string"""
    if isinstance(value, bool):
        return {True: "TRUE", False: "FALSE"}[value]
    else:
        return str(value)

def str2Bool(value):
    bools = {"TRUE": True, "FALSE": False}
    if value in bools:
        return bools[value]
    else:
        return value

def cookies2String(cookies):
    """Convert cookies to string data"""
    for cookie in cookies:
        subdomain = str(cookie.domain()).startswith(".")
        yield "\t".join([
            toString(cookie.domain()),
            toString(subdomain),
            toString(cookie.path()),
            toString(cookie.isSecure()),
            toString(cookie.expirationDate().toTime_t()),
            toString(cookie.name()),
            toString(cookie.value()),
        ])


def string2Cookies(lines):
    for txt in lines.splitlines():
        txt = txt.strip()
        if txt.startswith('#'):
            continue
        fields = map(str.strip, txt.split("\t"))
        if len(fields) == 7:
            domain, subdomain, path, secure, exp, name, value = fields
            cookie = QtNetwork.QNetworkCookie(name, value)
            cookie.setDomain(domain)
            cookie.setPath(path)
            cookie.setSecure(str2Bool(secure))
            cookie.setExpirationDate(QtCore.QDateTime.fromTime_t(int(exp)))
            yield cookie


class RENormalizer(object):
    """Normalizer which can convert text based on regex patterns"""

    def __init__(self, patterns):
        self.patterns = patterns
        self.transformers = map(self._cook, patterns)

    def _cook(self, pattern):
        if callable(pattern):
            return pattern
        regexp, replacement = pattern
        return lambda text: regexp.sub(replacement, text)

    def addPattern(self, pattern):
        patterns = list(self.patterns)
        patterns.append(pattern)
        self.transformers = map(self._cook, patterns)
        self.patterns = patterns

    def __call__(self, data):
        """Recursive normalize a SON instance, dict or text"""
        for normalizer in self.transformers:
            data = normalizer(data)
        # remove blank lines
        res = []
        append = res.append
        for line in data.split('\n'):
            if line:
                append(line)
        return '\n'.join(res)

    def pprint(self, data):
        """Pretty print data"""
        print self(data)


reNormalizer = RENormalizer([
   (re.compile(u"Server: [a-zA-Z0-9\/. ]+"),
               r"Server: ..."),
   (re.compile(u"Date: [a-zA-Z0-9:, ]+"),
               r"Date: ..."),
   (re.compile(u"User-Agent: [a-zA-Z0-9\/\\\(\);,. ]+"),
               r"User-Agent: ..."),
   (re.compile(u"JavaScript: typeof\(jQuery\)"),
               u""),
   (re.compile(u"JavaScript: typeof\(jQuery.simulate\)"),
               u""),
   (re.compile(u"Content-Length: [0-9]+"),
               u"Content-Length: ..."),
   (re.compile(u"Content-Type: multipart/form-data; boundary=----WebKitFormBoundary[a-zA-Z0-9]+"),
               r"Content-Type: multipart/form-data; boundary=----WebKitFormBoundary..."),
   ])


class ExtendedNetworkCookieJar(QtNetwork.QNetworkCookieJar):
    """Extended cookie handling"""

    def getMozillaCookies(self):
        """Return all cookies in Mozilla text format

        A typical line from the file might read (the spaces are tabs in the
        original file): 

        kb.mozillazine.org FALSE / FALSE 1146030396 wikiUserID 16993
        localhost FALSE / FALSE 2147472000 xeebobeta ...
        localhost FALSE / FALSE 4294967295 p01_sc_240269 ...

        The meaning of the above line is as follows:

        kb.mozillazine.org -- The name of the website (server) that stored the
            cookie.
        FALSE -- Whether the cookie can be read by other machines at the same
            domain (mozillazine.org); in this case, no.
        / -- The directory path for which the cookie is relevant; in this case,
            / denotes the home directory
            (i.e., the URL http://kb.mozillazine.org/).
        FALSE -- Whether the cookie requires a secure connection; in this case,
            no.
        1146030396 -- The time at which the cookie will expire (the number of
            seconds since 12 a.m., January 1, 1970).
        wikiUserID -- The name of the cookie.
        16993 -- The value of the cookie.
        
        see: http://kb.mozillazine.org/Cookies.txt for more information

        """
        return "\n".join(list(cookies2String(self.allCookies())))

    def setMozillaCookies(self, lines):
        """Set all cookies based on the given text input"""
        cookies = list(string2Cookies(lines))
        if cookies:
            self.setAllCookies(cookies)


# browser
class WebKitBrowser(object):
    """Headless web browser class based on QtWebKit using PySide"""

    def __init__(self, logLevel=INFO, logLevelPrint=NOTSET, downloadDir=".",
        enableJQuery=True, enableJQuerySimulate=True, jqName='$',
        eventDelay=0.01, ignoreSSLErrors=True, keepLogMessages=True,
        showLoadProgress=False, cookies=None, timeout=10,
        reNormalizer=reNormalizer):
        """Setup WebKit browser"""
        self._closed = False
        self.logLevel = logLevel
        self.logLevelPrint = logLevelPrint
        self.logMessages = []
        self.downloadDir = downloadDir
        self.enableJQuery = enableJQuery
        self.enableJQuerySimulate = enableJQuerySimulate
        self.jqName = jqName
        self.eventDelay = eventDelay
        self.ignoreSSLErrors = ignoreSSLErrors
        self.keepLogMessages = keepLogMessages
        self.showLoadProgress = showLoadProgress
        self.defaultTimeout = timeout
        self.reNormalizer = reNormalizer

        self.webview = None
        self.files = []
        self.errorCode = None
        self.errorMessage = None
        self.skipJavaScriptConsoleMessage = False

        # javascript
        if not self.jsSource:
            raise p01.tester.exceptions.ConfigurationError(
                "Missing source directory: %s" % self.self.jsSource)

        self.jQueryFileData = open(os.path.join(self.jsSource,
            self.jQueryFileName)).read()
        self.jQuerySimulateFileData = open(os.path.join(self.jsSource,
            self.jQuerySimulateFileName)).read()

        # setup settings
        settings = QtWebKit.QWebSettings.globalSettings()
        self.applySettings(settings)

        # setup webpage
        self.webpage = QtWebKit.QWebPage()
        self.applySettings(self.webpage.settings())

        # network access manager
        self.manager = QtNetwork.QNetworkAccessManager()
        self.manager.createRequest = self.doCreateRequest
        self.webpage.setNetworkAccessManager(self.manager)
        self.cookiesjar = ExtendedNetworkCookieJar()
        self.manager.setCookieJar(self.cookiesjar)
        # set initial cookie string
        if cookies is not None:
            self.setCookies(cookies)

        # network manager
        self.manager.connect(self.manager,
            QtCore.SIGNAL("sslErrors(QNetworkReply *, const QList<QSslError> &)"),
            self.onSSLErrors)
        self.manager.connect(self.manager,
            QtCore.SIGNAL('finished(QNetworkReply *)'),
            self.onReply)
        self.manager.connect(self.manager,
            QtCore.SIGNAL('authenticationRequired(QNetworkReply *, QAuthenticator *)'),
            self.onAuthenticationRequired)
        self._methodNames = dict(
            (getattr(QtNetwork.QNetworkAccessManager, "%sOperation" % s), s.lower())
            for s in ("Get", "Head", "Post", "Put"))

        # dispatch error handling
        self.webpage.javaScriptAlert = self.doJavaScriptAlert
        self.webpage.javaScriptConfirm = self.doJavaScriptConfirm
        self.webpage.javaScriptConsoleMessage = self.doJavaScriptConsoleMessage

        # webpage
        self.statuses = {}
        self._loadStatus = None
        self._replies = 0
        self.webpage.setForwardUnsupportedContent(True)
#        self.manager.connect(self.manager,
#            QtCore.SIGNAL('networkRequestCreated(QNetworkReply*)'),
#            self.onNetworkRequestCreated)
        self.webpage.connect(self.webpage,
            QtCore.SIGNAL("loadStarted()"),
            self.onLoadStarted)
        self.webpage.connect(self.webpage,
            QtCore.SIGNAL('unsupportedContent(QNetworkReply *)'),
            self.onUnsupportedContent)
        self.webpage.connect(self.webpage,
            QtCore.SIGNAL("loadProgress(int)"),
            self.onLoadProgress)
        self.webpage.connect(self.webpage,
            QtCore.SIGNAL('loadFinished(bool)'),
            self.onLoadFinished)
        self.webpage.connect(self.webpage,
            QtCore.SIGNAL("contentsChanged()"),
            self.onContentsChanged)

        # webframe
        self.webpage.connect(self.webframe,
            QtCore.SIGNAL("provisionalLoad()"),
            self.onProvisionalLoad)

        # headers
        self.headers = {}

        # lxml support
        self.xmlStrict = False
        self._etree = None
        self._normalized = None

    def applySettings(self, settings):
        settings.clearMemoryCaches()
        settings.setMaximumPagesInCache(0)
        settings.setObjectCacheCapacities(0, 0, 0)
        settings.setAttribute(QtWebKit.QWebSettings.LocalContentCanAccessRemoteUrls, True)
        settings.setAttribute(QtWebKit.QWebSettings.LocalContentCanAccessFileUrls, True)
        settings.setAttribute(QtWebKit.QWebSettings.JavascriptCanOpenWindows, True)
        settings.setAttribute(QtWebKit.QWebSettings.JavascriptCanAccessClipboard, True)

        settings.setAttribute(QtWebKit.QWebSettings.AutoLoadImages, False)
        settings.setAttribute(QtWebKit.QWebSettings.PrivateBrowsingEnabled, True)
        
        #settings.setAttribute(QtWebKit.QWebSettings.SiteSpecificQuirksEnabled, False)
        #settings.setAttribute(QtWebKit.QWebSettings.DeveloperExtrasEnabled, True)

    @property
    def jsSource(self):
        return pkg_resources.resource_filename('p01.tester', 'source')

    @property
    def jQueryFileName(self):
        return jQueryFileName

    @property
    def jQuerySimulateFileName(self):
        return jQuerySimulateFileName

    def doEventLoop(self, wait=None):
        if wait is None:
            wait = self.eventDelay
        app = p01.tester.testing.qApp # QtGui.QApplication.instance()
        if app is None:
            raise p01.tester.exceptions.UsageError(
                """QApplication not available, see setUpQApplication""")
        app.processEvents()
        time.sleep(wait)

    @property
    def webframe(self):
        if self._closed:
            raise p01.tester.exceptions.UsageError(
                """WebKitBrowser was closed, you need to setup another one""")
        return self.webpage.mainFrame()

    def doJavaScriptAlert(self, webframe, message):
        self.doLog(WARNING, "JavaScript alert: %s" % message)
        if self.webview is not None:
            QtWebKit.QWebPage.javaScriptAlert(self.webpage, webframe, message)

    def doJavaScriptConfirm(self, webframe, message):
        self.doLog(WARNING, "JavaScript confirm: %s" % message)
        if self.webview is not None:
            QtWebKit.QWebPage.javaScriptConfirm(self.webpage, webframe, message)

    def doJavaScriptPrompt(self, webframe, message, defaultValue):
        self.doLog(WARNING, "JavaScript promt: %s" % message)
        if self.webview is not None:
            QtWebKit.QWebPage.javaScriptPrompt(self.webpage, webframe, message, defaultValue)

    def doJavaScriptConsoleMessage(self, message, lineNumber, sourceID):
        if self.skipJavaScriptConsoleMessage:
            return
        if lineNumber:
            msg = "JavaScript error at line: %s %s %s " % (lineNumber,
                sourceID, message)
        else:
            msg = "JavaScript error: %s" % message
        self.doLog(ERROR, msg)

    def onSSLErrors(self, reply, errors):
        url = unicode(reply.url().toString())
        if self.ignoreSSLErrors:
            self.doLog(WARNING, "SSL certificate error ignored: %s" % url)
            reply.ignoreSslErrors()
        else:
            self.doLog(WARNING, "SSL certificate error: %s" % url)

#    def onNetworkRequestCreated(self, reply):
#        url = unicode(reply.url().toString())
#        self.doLog(INFO, "EVENT onNetworkRequestCreated %s" % url)
##        while not reply.atEnd ():
##            self.doEventLoop()
##            self.doLog(INFO, "..RUNNING onNetworkRequestCreated %s" % url)
#        self.doLog(INFO, "..reply.atEnd() %s" % reply.atEnd ())
#
#        end = time.time() + 0.5
#        while time.time() < end:
#            self.doEventLoop()
#
##        if reply.operation() == QtNetwork.QNetworkAccessManager.GetOperation:
##            self._networkGetReplies[0].append(reply)
##            url = QtCore.QUrl(reply.url())
##             copy url, qt nules it on return
##            networkReplyData = NetworkReplyData(self, url)
##            self._networkGetReplies[1].append(networkReplyData)
##            for signal, handler in self._networkReplySignals:
##                self.connect(reply, QtCore.SIGNAL(signal), handler)
##            self.emit(QtCore.SIGNAL('networkGetRequestCreated(int, QObject*)'),
##                self._networkGetReplies[0].index(reply), networkReplyData)

    # request handling
    def onLoadStarted(self):
        """Page load started"""
        self.statuses = {}
        self._loadStatus = None
        self.doLog(DEBUG, "Load started: %s" % (
            self.webframe.requestedUrl().toString()))

    def onProvisionalLoad(self):
        """Frame load started"""
        self.doLog(DEBUG, "Provisional load: %s" % (
            self.webframe.requestedUrl().toString()))

    def onLoadProgress(self, progress):
        if self.showLoadProgress:
            self.doLog(DEBUG, "Load progress: %s" % progress)

    def doCreateRequest(self, method, request, data):
        # first reset old etree and content
        isAsync = False
        self._etree = None
        self._normalized = None
        # create new request
        # log info
        methodName = self._methodNames[method].upper()
        url = unicode(request.url().toString())
        self.doLog(INFO, "Request: %s %s" % (methodName, url))
        for h in request.rawHeaderList():
            raw = "%s" % request.rawHeader(h)
            if raw == 'XMLHttpRequest':
                isAsync = True
                # set marker for XMLHTTPRequest
                self.doLog(INFO, "  XMLHTTPRequest invoked")
            self.doLog(INFO, "  %s: %s" % (h, raw))
        reply = QtNetwork.QNetworkAccessManager.createRequest(self.manager,
            method, request, data)
        if isAsync:
            # This is the missing part:
            # XMLHttpRequest get processed async and do not get applied to
            # doReply. Probably because they are not bound to the network
            # manager finished signal.
            while not reply.isFinished():
                self.doLog(DEBUG, "  XmlHttpRequest is running")
                self.doEventLoop()
            self.doLog(DEBUG, "  XmlHttpRequest isFinished()")
            self.onReply(reply)
            
        return reply

    def onReply(self, reply):
        self._replies += 1
        replyURL = unicode(reply.url().toString())
        if reply.error():
            self.doLog(ERROR, "Reply error: %s - %d (%s)" %
                (replyURL, reply.error(), reply.errorString()))
            self.errorCode = reply.error()
            self.errorMessage = reply.errorString()
        else:
            self.doLog(INFO, "Reply success: %s" % replyURL)
        self.headers = {}
        for header in reply.rawHeaderList():
            raw = "%s" % reply.rawHeader(header)
            if raw in ['application/json', 'application/json-rpc']:
                # set marker for XMLHTTPRequest
                self.doLog(INFO, "  XmlHttpRequest reply received")
            # use title-ized header names
            header = '-'.join([h.title() for h in str(header).split('-')])
            self.headers[str(header)] = raw
            self.doLog(INFO, "  %s: %s" % (header, raw))
        # set status per url
        status = str(reply.attribute(QtNetwork.QNetworkRequest.HttpStatusCodeAttribute))
        try:
            self.statuses[replyURL] = int(status) if status else None
        except Exception, e:
            self.statuses[replyURL] = status if status else None
        reply.close()
        reply.deleteLater()

    def onUnsupportedContent(self, reply, outfd=None):
        if not reply.error():
            self.doStartDownload(reply, outfd)
        else:
            self.doLog(ERROR, "Error on unsupported content: %s" % reply.errorString())

    def onContentsChanged(self):
        self.doLog(DEBUG, "Contents changed: %s" % self.url)

    def onLoadFinished(self, successful):
        self._loadStatus = successful
        status = {True: "successful", False: "error"}[successful]
        self.doLog(INFO, "Page load: %s %s (%d bytes)" %
            (status, self.url, len(self.html)))

    def onAuthenticationRequired(self, reply, authenticator):
        url = unicode(reply.url().toString())
        realm = unicode(authenticator.realm())
        self.doLog("HTTP auth required: %s (realm: %s)" % (url, realm))
        credentials = self.getCredentials(url, realm)
        if credentials is not None:
            user, password = credentials
            self.doLog(DEBUG, "HTTP auth credentials: %s/%s" %
                (user, "*"*len(password)))
            authenticator.setUser(user)
            authenticator.setPassword(password)
        else:
            self.doLog(WARNING, "HTTP auth callback returned no credentials")

    def onWebViewDestroyed(self, window):
        self.webview = None

    # authentication support
    def getCredentials(self, url, realm):
        """Return a username, password tuple based on the given url and realm"""
        raise NotImplementedError("Subclass must implement getCredentials")

    # wait on load
    def waitOnLoad(self, timeout=None):
        """Wait on page load till _loadStatus is set by onLoadFinished"""
        self.doLog(DEBUG, "Wait on load started")
        if timeout is None:
            # no timeout makes no sence
            timeout = self.defaultTimeout

        self.doEventLoop(0.0)
        if self._loadStatus is not None:
            status = self._loadStatus
            self._loadStatus = None
            self.doLog(DEBUG, "Wait on load without loop")
            return status

        end = time.time() + timeout
        while self._loadStatus is None:
            if time.time() > end:
                self.doLog(ERROR, "Wait on load timeout: %d seconds" % timeout)
                raise p01.tester.exceptions.TimeoutError(
                    "timeout: %d seconds" % timeout)
            self.doEventLoop()

        self.doEventLoop(0.0)
        status = self._loadStatus
        if status:
            self.doLog(DEBUG, "Wait on load after loop")
            self.applyJavaScripts()
            self.webpage.setViewportSize(self.webframe.contentsSize())

        self._loadStatus = None
        return status

    # wait on ajax
    def waitOnCallback(self, replies, timeout=None):
        """Wait on ajax callback till the amount of replies is reached"""
        self.doLog(DEBUG, "Wait on callback started")
        if timeout is None:
            # no timeout makes no sence
            timeout = self.defaultTimeout

        end = time.time() + timeout
        while self._replies < replies:
            if time.time() > end:
                self.doLog(ERROR, "Error wait on callback timeout: %d seconds" %
                    timeout)
                break
#                raise p01.tester.exceptions.TimeoutError(
#                    "timeout: %d seconds" % timeout)
            else:
                self.doEventLoop()

        self.doEventLoop(0.0)
        self.doLog(DEBUG, "Wait on callback after loop")

    def wait(self, timeout):
        """Wait timeout"""
        end = time.time() + timeout
        while time.time() < end:
            self.doEventLoop()
        self.doEventLoop(0.0)

    # browser interaction
    def open(self, url):
        """Open an url"""
        self.doEventLoop()
        url = QtCore.QUrl(url) 
        self.webframe.load(url)
        self.waitOnLoad()

    def setHtml(self, html, baseURL=None):
        self.webframe.setHtml(html, baseURL)

    def close(self):
        """Close browser and everything else"""
        self.doEventLoop()
        if self.cookiesjar:
            self.cookiesjar = None
        if self.webpage:
            self.webpage = None
        if self.webview:
            self.closeWebView()
        if self.manager:
            self.manager = None
        if self._etree:
            self._etree = None
        self._closed = True

    @property
    def html(self):
        """Returns HTML from current page."""
        if self.webframe:
            return unicode(self.webframe.toHtml())

    @property
    def document(self):
        """Returns HTML from current page."""
        if self.webframe:
            return unicode(self.webframe.documentElement().toOuterXml())

    @property
    def url(self):
        """Returns URL from current page."""
        if self.webframe:
            return unicode(self.webframe.url().toString())

    @property
    def status(self):
        """Return the HTTP status code received for the current location."""
        return self.statuses.get(self.url)

    @property
    def contentType(self):
        """Return the Content-Type for the current location."""
        return self.headers.get('Content-Type')

    def renderTreeDump(self):
        """Dispatch renderTreeDump call to frame"""
        return self.webframe.renderTreeDump()

    # JQuery API
    def js(self, code, returnResult=True, waitOnCallback=False,
        waitOnLoad=False, timeout=None, logging=True):
        """Evaluate javascript in browser"""
        # prepare callback checker
        if isinstance(waitOnCallback, int):
            replies = self._replies + waitOnCallback
        else:
            replies = self._replies + 1
        # do javascript call
        self.fakeEvaluateJavaScript()
        if logging:
            self.doLog(INFO, "JavaScript: %s" % code)
        self.skipJavaScriptConsoleMessage = True
        res = self.webframe.evaluateJavaScript(code)
        if waitOnCallback and waitOnLoad:
            raise p01.tester.exceptions.UsageError(
                "Cannot use waitOnCallback and waitOnLoad at the same time")
        elif waitOnCallback:
            self.waitOnCallback(replies, timeout)
        elif waitOnLoad:
            self.waitOnLoad(timeout)
        elif timeout:
            self.wait(timeout)
        self.skipJavaScriptConsoleMessage = False
        if returnResult:
            return res

    def click(self, selector, waitOnCallback=True, waitOnLoad=False,
        timeout=None):
        """Click a button using simulate"""
        # let self.js() do the work
        js = '%s("%s").simulate("click");' % (self.jqName, escape(selector))
        self.js(js, False, waitOnCallback, waitOnLoad, timeout)

    def val(self, selector, value=None):
        """Set or get a value using a jQuery selector"""
        if value is not None:
            js = '%s("%s").val("%s");' % (self.jqName, escape(selector),
                escape(value))
            self.js(js)
        else:
            js = '%s("%s").val();' % (self.jqName,  escape(selector))
            return self.js(js)

    def check(self, selector, status=True):
        """Check an input checkbox using a jQuery selector."""
        if status:
            s = 'true'
        else:
            s = 'false'
        js = '%s("%s").attr("checked", %s)' % (self.jqName,  escape(selector), s)
        self.js(js)

    def choose(self, selector, value):
        """Choose a radio input using a jQuery selector."""
        js = '%s("%s").filter("[value=%s]").simulate("click")' % (self.jqName,
             escape(selector),  escape(value))
        self.js(js)

    def select(self, selector):
        """Choose a option in a select using a jQuery selector."""
        js = '%s("%s").attr("selected", "selected")' % (self.jqName,
            escape(selector))
        self.js(js)

    # WebKit API
    def wkClickElement(self, element, waitOnCallback=False, waitOnLoad=False,
        timeout=None):
        """Click an element using WebKit.click()"""
        # prepare callback checker
        if isinstance(waitOnCallback, int):
            replies = self._replies + waitOnCallback
        else:
            replies = self._replies + 1
        # do javascript call
        js = (
            '(function(el) {'
            '  var e = document.createEvent("MouseEvents");'
            '  e.initEvent("click", true, true );'
            '  this.dispatchEvent(e);'
            '})(this);'
        )
        self.doLog(INFO, "JavaScript: %s" % js)
        element.evaluateJavaScript(js)
        if waitOnCallback and waitOnLoad:
            raise p01.tester.exceptions.UsageError(
                "Cannot use waitOnCallback and waitOnLoad at the same time")
        elif waitOnCallback:
            self.waitOnCallback(replies, timeout)
        elif waitOnLoad:
            self.waitOnLoad(timeout)
        elif timeout:
            self.wait(timeout)

    def wkClick(self, selector, waitOnCallback=False, waitOnLoad=False,
        timeout=10):
        """Click a CSS2 selector element using WebKit.click()"""
        element = self.webframe.findFirstElement(selector)
        self.wkClickElement(element, waitOnCallback, waitOnLoad, timeout)

    def wkValue(self, selector, value=None):
        """Text input value handling using a WebKit element selector"""
        element = self.webframe.findFirstElement(selector)
        if value is None:
            js = 'this.value'
            self.doLog(INFO, "JavaScript: %s" % js)
            return element.evaluateJavaScript(js)
        else:
            js = 'this.value = "%s"' % value
            self.doLog(INFO, "JavaScript: %s" % js)
            element.evaluateJavaScript(js)

    def wkCheckElement(self, element, status=True):
        """check an input checkbox using a webkit element."""
        if status:
            js = "this.checked=true;"
        else:
            js = "this.checked=false;"
        self.doLog(INFO, "JavaScript: %s" % js)
        element.evaluateJavaScript(js)
 
    def wkCheck(self, selector, status=True):
        """Check an input checkbox based on status using a css selector."""
        element = self.webframe.findFirstElement(selector)
        return self.wkCheckElement(element, status)
    
    # webview makes browser visible
    def openWebView(self):
        """Create a QWebView object and insert current QWebPage."""
        if self.webview:
            raise p01.tester.exceptions.UsageError(
                "Cannot create webview (already initialized)")
        self.webview = QtWebKit.QWebView()
        self.webview.setPage(self.webpage)
        window = self.webview.window()
        window.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        window.connect(window, QtCore.SIGNAL('destroyed(QObject *)'),
            self.onWebViewDestroyed)
        self.webview.show()

    def closeWebView(self):
        """Close current QWebView."""
        if self.webview:
            self.webview.close()
            self.webview =None

    def show(self):
        """Show browser page and loop till closed"""
        self.openWebView()
        while self.webview:
            self.doEventLoop()

    def visible(self):
        """Run in visible mode without to block"""
        self.openWebView()

    def inspect(self):
        """Start an inspector"""
        if self.webview is None:
            self.openWebView()
        self.webview.settings().setAttribute( 
            QtWebKit.QWebSettings.WebAttribute.DeveloperExtrasEnabled, True) 
        inspect = QtWebKit.QWebInspector() 
        inspect.setPage(self.webview.page()) 
        inspect.show()
        while self.webview:
            self.doEventLoop() 

    # cookies
    def getCookies(self):
        """Return string containing the current cookies in Mozilla format."""
        return self.cookiesjar.getMozillaCookies()

    def setCookies(self, cookies):
        """Set cookies from a string with Mozilla-format cookies."""
        return self.cookiesjar.setMozillaCookies(cookies)

    # download files
    def download(self, url):
        """Download from given URL"""
        def _onReply(reply):
            url = unicode(reply.url().toString())
            self._downloadReplyStatus = not bool(reply.error())
        self._downloadReplyStatus = None
        if not urlparse.urlsplit(url).scheme:
            url = urlparse.urljoin(self.url, url)
        request = QtNetwork.QNetworkRequest(QtCore.QUrl(url))
        # Create a new manager to process this download
        manager = QtNetwork.QNetworkAccessManager()
        # create a copy of the cookies jar to prevent
        # CJ to be garbage collected
        cj = ExtendedNetworkCookieJar()
        cj.setAllCookies(self.cookiesjar.allCookies())
        manager.setCookieJar(cj)
        reply = manager.get(request)
        if reply.error():
            raise p01.tester.exceptions.DownloadError(
                "Download error: %s" % reply.errorString())
        reply.downloaded_nbytes = 0
        manager.connect(manager, QtCore.SIGNAL('finished(QNetworkReply *)'), _onReply)
        out = StringIO()
        self.doStartDownload(reply, out)
        while self._downloadReplyStatus is None:
            self.doEventLoop()
        return out.getvalue()

    # screenshot
    def screenshot(self, frmt=None):
        """Get screenhot as QImage"""
        if frmt is None:
            frmt = QtGui.QImage.Format_ARGB32
        img = QtGui.QImage(self.webpage.viewportSize(), frmt)
        painter = QtGui.QPainter(img)
        self.webpage.mainFrame().render(painter)
        # release and return
        painter.end()
        return image

    # lxml API
    @property
    def etree(self):
        if self._etree is not None:
            return self._etree
        if self.xmlStrict:
            self._etree = lxml.etree.fromstring(self.html,
                parser=lxml.etree.XMLParser(resolve_entities=False))
        else:
            encoding = 'UTF-8'
            contentType = self.headers.get('Content-Type')
            if contentType is not None:
                match = RE_CHARSET.match(contentType)
                if match is not None:
                    encoding = match.groups()[0]
            parser = lxml.etree.HTMLParser(encoding=encoding,
                remove_blank_text=True, remove_comments=True, recover=True)
            self._etree = lxml.etree.fromstring(self.html, parser=parser)
        return self._etree

    # xpath API
    def getXPathSelector(self, namespaces=None):
        """Returns an XPathSelector instance"""
        return p01.tester.xpath.XPathSelector(self.etree, namespaces=namespaces)

    # logging support
    def doLog(self, level, msg):
        # don't log NOTSET
        if self.logLevel != NOTSET and self.logLevel <= level:
            if level == INFO:
                logger.info(msg)
            elif level == DEBUG:
                logger.debug(msg)
            if self.keepLogMessages:
                # keep the log messages
                self.logMessages.append(msg)
        if self.logLevelPrint != NOTSET and self.logLevelPrint <= level:
            print msg

    def resetLogMessages(self):
        self.logMessages = []

    @property
    def log(self):
        """Read and reset log messages"""
        res = '\n'.join(self.logMessages)
        self.resetLogMessages()
        if self.reNormalizer is not None:
            res = self.reNormalizer(res)
        return res

    # issue workarround
    def fakeEvaluateJavaScript(self):
        """Workarround with invalid evaluateJavaScript call"""
        # XXX: it seems that this is issue is gone in PySide 1.2.0
        # XXX: workarround for evaluateJavaScript issue!!!
        # Send invalid js call which forces to reset the engine or something
        # like that. This seems to be an issue, without this every other JS call
        # will fail. Just use return outside a function call for force an JS
        # error. Also skip error handling during this call
        pass
        #oldLogLevel = self.logLevel
        #self.logLevel = NOTSET
        #self.webframe.evaluateJavaScript('return true;')
        #self.logLevel = oldLogLevel

    # helper
    def isJQueryLoaded(self):
        # check if jQuery is available
        return self.js("typeof(jQuery)") != 'undefined'

    def isJQuerySimulateLoaded(self):
        if self.isJQueryLoaded():
            return self.js("typeof(jQuery.simulate)") != 'undefined'
        else:
            return False

    def applyJQuery(self):
        """Apply jquery to current frame if enable and not loaded"""
        if self.enableJQuery and not self.isJQueryLoaded():
            self.fakeEvaluateJavaScript()
            self.webframe.evaluateJavaScript(self.jQueryFileData)
            self.doLog(DEBUG, "Apply JQuery")

    def applyJQuerySimulate(self):
        """Apply jquery simulate to current frame if enable and not loaded"""
        if self.enableJQuerySimulate and not self.isJQuerySimulateLoaded():
            self.fakeEvaluateJavaScript()
            self.webframe.evaluateJavaScript(self.jQuerySimulateFileData)
            self.doLog(DEBUG, "Apply JQuery simulate")

    def applyJavaScripts(self):
        """Apply javascripts if enable and not loaded"""
        self.applyJQuery()
        self.applyJQuerySimulate()

    def _getFilePathForURL(self, url, reply=None):
        urlinfo = urlparse.urlsplit(url)
        folder = urlinfo.netloc.replace(':', '_')
        path = os.path.join(os.path.abspath(self.downloadDir), folder)
        if urlinfo.path != '/':
            p = urlinfo.path
            if len(p) > 2:
                if p[0] == '/':
                    p = p[1:]
            path = os.path.join(path, p)
        if reply.hasRawHeader('content-disposition'):
            cd = '%s' % reply.rawHeader('content-disposition')
            pattern = 'attachment;filename=(.*)'
            if re.match(pattern, cd):
                filename = re.sub('attachment;filename=(.*)', '\\1', cd)
                path = os.path.join(path, filename)
        if not os.path.isdir(os.path.dirname(path)):
            os.makedirs(os.path.dirname(path))
        if path is None:
            raise p01.tester.exceptions.ConfigurationError(
                "Download mode is unknown, can't determine the final filename")
        return path

    def doStartDownload(self, reply, outfd):
        url = unicode(reply.url().toString())
        path = None
        if outfd is None:
            path = self._getFilePathForURL(url, reply)
            outfd = open(path, "wb")
        def _on_ready_read():
            data = reply.readAll()
            if getattr(reply, 'downloaded_nbytes', None) is None:
                reply.downloaded_nbytes= 0
            reply.downloaded_nbytes += len(data)
            outfd.write(data)
            self.doLog(INFO, "Read from download stream (%d bytes): %s"
                % (len(data), url))
        def _on_network_error():
            self.debug(ERROR, "Network error on download: %s" % url)
        def _on_finished():
            if path is not None:
                outfd.flush()
                dict(self.files)[path]['finished'] = True
            self.doLog(DEBUG, "Download finished: %s" % url)
        if path is not None:
            self.files.append((path, {'reply':reply,'finished':False,}))
        reply.connect(reply, QtCore.SIGNAL("readyRead()"), _on_ready_read)
        reply.connect(reply, QtCore.SIGNAL("NetworkError()"), _on_network_error)
        reply.connect(reply, QtCore.SIGNAL("finished()"), _on_finished)
        self.doLog(DEBUG, "Download: %s" % url)
