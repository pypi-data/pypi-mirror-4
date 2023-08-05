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
$Id: exceptions.py 3131 2012-09-29 20:08:46Z roger.ineichen $
"""
__docformat__ = "reStructuredText"


class WebKitBrowserError(Exception):
    """WebKitBrowserError error base class"""

class ConfigurationError(WebKitBrowserError):
    """WebKitBrowser configuration error"""

class ElementLookupError(WebKitBrowserError):
    """Element lookup error"""

class UsageError(WebKitBrowserError):
    """WebKitBrowser usage error."""

class DownloadError(WebKitBrowserError):
    """WebKitBrowser download error"""

class TimeoutError(WebKitBrowserError):
    """A timeout (usually on page load) has been reached."""
