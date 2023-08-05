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
$Id: testing.py 3131 2012-09-29 20:08:46Z roger.ineichen $
"""
__docformat__ = "reStructuredText"

import time
import logging
import re

import qt_compat
QtCore = qt_compat.QtCore
QtGui = qt_compat.import_module("QtGui")

qApp = None


def setUpQApplication():
    global qApp
    qApp = QtGui.QApplication.instance()
    if qApp is None:
        qApp = QtGui.QApplication([])
    return qApp

def tearDownQApplication():
    global qApp
    qApp = QtGui.QApplication.instance()
    if qApp is not None:
        qApp.quit()
        # remove singleton reference
        # see: http://stuvel.eu/blog/127/multiple-instances-of-qapplication-in-one-process
        # see: http://pastebin.com/9RkdhMiP
        #QtGui.qApp = None
        #qApp = None


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
        """Normalize a dict or text"""
        if not isinstance(data, basestring):
            data = pprint.pformat(data)
        for normalizer in self.transformers:
            data = normalizer(data)
        return data

    def pprint(self, data):
        """Pretty print data"""
        if isinstance(data, list):
            for item in data:
                print self(item)
        else:
            print self(data)


reNormalizer = RENormalizer([
   (re.compile(u"[0-9]+/[a-zA-Z]+/[0-9]+ [0-9]+:[0-9]+:[0-9]+"),
               r".../.../... ...:...:..."),
   (re.compile(u":[0-9]+ "),  r":... "),
   ])


class LoggingHandler(logging.Handler):
    """Simple logging handler which will temporary install itself"""

    def __init__(self, name, level=1, normalizer=None):
        logging.Handler.__init__(self)
        self.name = name
        if normalizer is None:
            normalizer = reNormalizer
        self.reNormalizer = normalizer
        self.records = []
        self.setLoggerLevel(level)
        self.install()

    def setLoggerLevel(self, level=1):
        self.level = level
        self.oldlevels = {}

    def emit(self, record):
        self.records.append(record)

    def clear(self):
        del self.records[:]

    def install(self):
        """Uninstall current logger if any and install our logger"""
        logger = logging.getLogger(self.name)
        self.oldlevels[self.name] = logger.level
        logger.setLevel(self.level)
        logger.addHandler(self)

    def uninstall(self):
        """Uninstall our logger and install previous installed logger"""
        logger = logging.getLogger(self.name)
        logger.setLevel(self.oldlevels[self.name])
        logger.removeHandler(self)

    def getLines(self, record):
        """Returns the message lines for a given record"""
        return '\n'.join([line
                          for line in record.getMessage().split('\n')
                          if line.strip()])

    def __str__(self):
        return '\n'.join(
            ["%s %s" % (record.levelname, self.getLines(record))
             for record in self.records]
            )

    @property
    def normalized(self):
        """Returns the normalized output"""
        return self.reNormalizer(str(self))


def getLogger(name, level=1, normalizer=None):
    return LoggingHandler(name, level=1, normalizer=None)
