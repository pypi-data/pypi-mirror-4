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
$Id: server.py 3131 2012-09-29 20:08:46Z roger.ineichen $
"""
__docformat__ = "reStructuredText"

import threading
import logging
import wsgiref.simple_server

logger = logging.getLogger('p01.tester.server')


class WSGIRequestHandler(wsgiref.simple_server.WSGIRequestHandler):
    """WSGI request handler with HTTP/1.1 and automatic keepalive"""

    # set to HTTP/1.1 to enable automatic keepalive
    protocol_version = "HTTP/1.1"

    def address_string(self):
        """Return the client address formatted for logging.

        We only use host and port without socket.getfqdn(host) for a
        simpler test output.

        """
        host, port = self.client_address[:2]
        return '%s:%s' % (host,port)

    def _log(self, level, msg):
        """write log to our logger"""
        logger.log(level, msg)

    def log_error(self, format, *args):
        """Write error message log to our logger using ERROR level"""
        msg = "%s - - [%s] %s\n" % (self.address_string(),
            self.log_date_time_string(), format%args)
        self._log(logging.ERROR, msg)

    def log_message(self, format, *args):
        """Write simple message log to our logger usning INFO level"""
        msg = "%s - - [%s] %s\n" % (self.address_string(),
            self.log_date_time_string(), format%args)
        self._log(logging.INFO, msg)


class WSGIRunner(threading.Thread):
    """WSGI runner"""

    def __init__(self, app, host, port):
        super(WSGIRunner, self).__init__()
        self.host = host
        self.port = port
        self.server = wsgiref.simple_server.make_server(self.host, 
            int(self.port), app, handler_class=WSGIRequestHandler)
        self.server.timeout = 0.5
        self.stopping = False

    def run(self):
        while not self.stopping:
            self.server.handle_request()


class WSGIServer(object):
    """WSGI Server"""

    def __init__(self, name, app, host, port):
        self.name = name
        self.app = app
        self.host = host
        self.port = port
        self.runner = None

    def start(self):
        if self.runner is None:
            self.runner = WSGIRunner(self.app, self.host, self.port)
            self.runner.start()

    def stop(self):
        if self.runner is not None:
            self.runner.stopping = True
            self.runner.join()
            self.runner = None


WSGI_SERVERS = None

def startWSGIServer(name, app, host='localhost', port='9090'):
    """Serve a WSGI aplication on the given host and port referenced by name"""
    global WSGI_SERVERS
    if WSGI_SERVERS is None:
        WSGI_SERVERS = {}
    for data in WSGI_SERVERS.values():
        if data['host'] == host and data['port'] == port:
            raise ValueError("WSGI server already running at: %s:%s" % (host,
                port))
    server = WSGIServer(name, app, host, port)
    server.start()
    WSGI_SERVERS[name] = {'host': host, 'port': port, 'server': server}


def stopWSGIServer(name):
    """Stop WSGI server by given name reference"""
    global WSGI_SERVERS
    if WSGI_SERVERS is not None:
        server = WSGI_SERVERS[name]['server']
        server.stop()
        del WSGI_SERVERS[name]


def getWSGIApplication(name):
    """Returns the application refenced by name"""
    global WSGI_SERVERS
    if WSGI_SERVERS is not None:
        server = WSGI_SERVERS[name]['server']
        return server.app
