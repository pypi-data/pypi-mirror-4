# vim:fileencoding=utf-8
# Copyright (c) 2008 gocept gmbh & co. kg
# See also LICENSE.txt
# 
"""General utility functions."""

# Python imports
from urlparse import urlparse, urlunparse, urljoin
from sgmllib import SGMLParseError
import lxml.etree
import md5
import formatter
import StringIO

# CMF/Plone imports
from Products.CMFCore.utils import getToolByName
from Products.Archetypes.public import RichWidget

# Zope imports
import gocept.linkchecker.log as log
from StructuredText import Basic
from StructuredText.DocumentClass import StructuredTextLink, DocumentClass

# Sibling imports
from gocept.linkchecker import lchtmllib


inet_services = {
    'ftp': 21,
    'http': 80,
    'https': 443,
    }


class urlrecord:
    """Representation of a URL with an attribute for each component.
    """

    components = ('scheme', 'netloc', 'path', 'parameters', 'query', 'fragment')

    def __init__(self, url):
        url_components = urlparse(url)

        for i, c in enumerate(self.components):
            setattr(self, c, url_components[i])

    def __str__(self):
        url_components = [getattr(self, c, '') for c in self.components]
        url = urlunparse(url_components)
        return url


def resolveRelativeLink(url, context):
    """Normalizes a URL according to RfC 2396 and throws away the fragment
    component, if any.
    """
    url_ = urlrecord(url)

    if url_.scheme:
        # Url has a protocol specified, e.g. HTTP, so we need not complete it.
        # We're only interested in a few protocols, though.
        if url_.scheme.lower() not in ['http', 'https', 'ftp']:
            return url
    elif url_.netloc:
        # A host is given, so we assume the HTTP protocol.
        url_.scheme = 'http'
    else:
        # We only have a path. We join it with the configured prefix (or use the
        # request if nothing was specified).
        lc = getToolByName(context, "portal_linkchecker")
        prefix = lc.database.defaultURLPrefix or context.REQUEST.BASE0
        if prefix.endswith('/'):
            prefix = prefix[:-1]
        portal_url = getToolByName(context, 'portal_url')
        prefix += '/%s' % portal_url.getRelativeContentURL(context)
        # Make up for a deviation of Python's urljoin from the test cases given
        # in RfC 2396, Appendix C.
        if url.startswith('?'):
            url = './' + url

        url = urljoin(prefix, url)
        url_ = urlrecord(url)

    url_.scheme = url_.scheme.lower()
    url_.netloc = url_.netloc.lower()

    if ':' in url_.netloc:
        hostname, port = url_.netloc.split(':')
        if port == str(inet_services.get(url_.scheme)):
            url_.netloc = hostname

    if not url_.path:
        url_.path = '/'

    url_.fragment = ''

    new_url = str(url_)
    return new_url


def retrieveSTX(text):
    """Retrieve links from STX data."""
    data = Basic(text)
    data = DocumentClass()(data)
    
    stack = data.getChildren()
    links = []
    while stack:
        element = stack.pop()
        if isinstance(element, StructuredTextLink):
            # Handle images seperately
            element = element.href
            if element.startswith('img:'):
                element = element[4:]
            links.append(element)
        try:
            stack.extend(element.getChildren())
        except AttributeError:
            pass

    return links


def retrieveHTML(text):
    parser = lchtmllib.LCHTMLParser(formatter.NullFormatter())
    try:
        parser.feed(text)
        parser.close()
    except SGMLParseError, e:
        # SGMLLib seems to die on bad HTML sometimes. (At least with python2.1)
        log.logger.error('retrieveHTML failed due to SGMLParseError: %s' % str(e))
    return tuple(parser.anchorlist) + tuple(parser.imglist)


def retrieveOneRichTextField(object, field):
    """
    Helper function for retrieveAllRichTextFields below and possibly
    useful for others.

    We would want to check something like
    (object.Schema()[fieldname].text_format
    but that attribute does not exist.
    Just try both retrieveSTX and retrieveHTML then.
    """
    text = field.getRaw(object)
    links = []

    for link in retrieveSTX(text):
        links.append(link)

    for link in retrieveHTML(text):
        links.append(link)
    return links


def retrieveAllRichTextFields(object):
    """Looks for all AT fields on an object that use the RichWidget
    and retrieves their links.
    """
    links = []
    for field in _getRichTextFields(object):
        for link in retrieveOneRichTextField(object, field):
            links.append(link)
    return links


## Update helpers

def updateAllRichTextFields(old_url, new_url, object):
    """Looks for all AT fields on an object that use the RichWidget
    and updates all occurances of the given url.
    """
    for field in _getRichTextFields(object):
        updateOneRichTextField(old_url, new_url, object, field)
    object.reindexObject()


def updateOneRichTextField(old_url, new_url, object, field):
    """Updates all occurances of old_url with new_url."""
    text = field.getRaw(object).decode('utf-8')
    # We can only handle HTML now.
    text = u"""<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
    <linkcheckerroot912ec803b2ce49e4a541068d495ab570>%s</linkcheckerroot912ec803b2ce49e4a541068d495ab570>""" % text
    parser = lxml.etree.HTMLParser()
    tree = lxml.etree.parse(StringIO.StringIO(text), parser)
    # links
    for link in tree.getiterator("a"):
        if link.get("href") == old_url:
            link.set("href", new_url)
    # images
    for image in tree.getiterator("img"):
        if image.get("src") == old_url:
            image.set("src", new_url)
    text = lxml.etree.tostring(tree, encoding=unicode)
    text = text.replace('\n<html xmlns="http://www.w3.org/1999/xhtml"><body><linkcheckerroot912ec803b2ce49e4a541068d495ab570>', '')
    text = text.replace('</linkcheckerroot912ec803b2ce49e4a541068d495ab570></body></html>', '')
    field.set(object, text)


def _getRichTextFields(object):
    return [f for f in object.Schema().fields()
              if isinstance(f.widget, RichWidget)]


def hash_link(link, object):
    """Provides a hash which can be used as an id for a Link object."""
    uid = object.UID()
    if link is None:
        link = ""
    if isinstance(link, unicode):
        link = link.encode('utf-8')
    return md5.md5("%s:%s" % (link, uid)).hexdigest()


def hash_url(url):
    if isinstance(url, unicode):
        url = url.encode('utf-8')
    return md5.md5(url).hexdigest()
