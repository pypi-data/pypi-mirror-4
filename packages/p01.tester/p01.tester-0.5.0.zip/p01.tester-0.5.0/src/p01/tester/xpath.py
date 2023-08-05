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
$Id: xpath.py 3131 2012-09-29 20:08:46Z roger.ineichen $
"""
__docformat__ = "reStructuredText"

from lxml import etree


# xpath handling internals
def toStr(text, encoding='UTF-8'):
    """Return the str representation of text in the given encoding. Unlike
    .encode(encoding) this function can be applied directly to a str
    object without the risk of double-decoding problems (which can happen if
    you don't use the default 'ascii' encoding)
    """
    if isinstance(text, unicode):
        return text.encode(encoding)
    elif isinstance(text, str):
        return text
    else:
        raise TypeError(
            "Must get an unicode or str object, got %s" % type(text).__name__)


def flatten(x):
    """flatten(sequence) -> list

    Returns a single, flat list which contains all elements retrieved
    from the sequence and all recursively contained sub-sequences
    (iterables).

    Examples:
    >>> [1, 2, [3,4], (5,6)]
    [1, 2, [3, 4], (5, 6)]
    >>> flatten([[[1,2,3], (42,None)], [4,5], [6], 7, (8,9,10)])
    [1, 2, 3, 42, None, 4, 5, 6, 7, 8, 9, 10]"""

    result = []
    for el in x:
        if hasattr(el, "__iter__"):
            result.extend(flatten(el))
        else:
            result.append(el)
    return result


def getRoot(content, encoding='UTF-8'):
    parser = etree.HTMLParser(encoding=encoding, remove_blank_text=True,
        remove_comments=True, recover=True)
    return etree.fromstring(content, parser=parser)


def tostring(e):
    if isinstance(e, etree._Element) and e.tag == 'br':
        # a <br /> tag contains the text after the tag. just return
        # '<br />' here (with_tail=False)
        rv = etree.tostring(e, method='html', with_tail=False, encoding=unicode)
    elif isinstance(e, (tuple, list)):
        rv = ''.join([tostring(ee) for ee in e])
    else:
        rv = etree.tostring(e, method='html', encoding=unicode)
    #fixup 0xa0 -> &nbsp;
    rv = rv.replace(u'\xa0', '&nbsp;')
    return rv


def tostring2(e):
    if isinstance(e, (tuple, list)):
        rv = ''.join([tostring2(ee) for ee in e])
    else:
        rv = etree.tostring(e, method='html', encoding=unicode)
    #fixup 0xa0 -> &nbsp;
    rv = rv.replace(u'\xa0', '&nbsp;')
    return rv


class XPathSelectorList(list):
    """XPath selector list"""

    def __getslice__(self, i, j):
        return self.__class__(list.__getslice__(self, i, j))

    def select(self, xPath):
        return self.__class__(flatten([x.select(xPath) for x in self]))

    def extract(self, xPath=None, strip=False):
        if strip:
            return u'\n'.join([x.extract(xPath).strip() for x in self])
        else:
            return u''.join([x.extract(xPath) for x in self])


class XPathSelector(object):
    """XPath selector for HTML"""

    def __init__(self, root, namespaces=None):
        self.root = root
        self.namespaces = namespaces
        try:
            self.evaluator = etree.XPathEvaluator(self.root,
                namespaces=self.namespaces)
        except TypeError:
            # root is already a string result
            pass

    def xpath(self, xPath):
        try:
            root = self.evaluator(xPath)
        except etree.XPathError:
            raise ValueError("Invalid XPath: %s" % xPath)
        if hasattr(root, '__iter__'):
            res = root
        else:
            res = [root]
        return res

    def select(self, xPath):
        res = self.xpath(xPath)
        res = [self.__class__(x, self.namespaces) for x in res]
        return XPathSelectorList(res)

    def extract(self, xPath=None, strip=False):
        if xPath is None:
            if isinstance(self.root, str):
                return unicode(self.root)
            elif isinstance(self.root, unicode):
                return self.root
            else:
                return tostring(self.root)
        else:
            xsl = self.select(xPath)
            return xsl.extract(strip=strip)

    def extractContent(self, xPath):
        """Extract the content of the specified element, but not the element"""
        els = self.xpath(xPath)
        return ''.join((el.text or u'')+tostring2(el.getchildren()) for el in els)

    def __nonzero__(self):
        return bool(self.extract())

    def __str__(self):
        data = repr(self.extract()[:40])
        return "<%s data=%s...>" % (type(self).__name__, data)

    __repr__ = __str__


def getXPathSelector(content, encoding='UTF-8', namespaces=None):
    """Returns an XPathSelector instance"""
    root = getRoot(content, encoding)
    return XPathSelector(root, namespaces=namespaces)
