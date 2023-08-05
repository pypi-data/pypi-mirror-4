# Copyright (c) 2004-2005 gocept gmbh & co. kg
# See also LICENSE.txt
# 

import unittest

from Products.Archetypes.tests.common import *
from Products.Archetypes.tests.utils import *

from gocept.linkchecker.tests.base import LinkCheckerTestCase

from Products.CMFCore.utils import getToolByName


class LinkCheckerTest(LinkCheckerTestCase):

    def test_normalization(self):
        # Test if relative link will get absolute in Database
        self.loginAsPortalOwner()
        portal = self.portal
        pl = getToolByName(portal, 'portal_linkchecker')
	pl.database.defaultURLPrefix = portal.absolute_url()

        portal.invokeFactory('Document', 'doc1')
        
        doc1 = portal.doc1
        doc1.setText('bla<a href="index_html">index.html</a>\nbumm')
        pl.retrieving.retrieveObject(doc1)
        db_cont = pl.database.queryLinks()
        self.assertEqual(1, len(db_cont))
        self.assertEqual(portal.absolute_url() + "/index_html", db_cont[0].url)

        
        ## assert '..' are stripped
    
        portal.invokeFactory('Folder', 'f1')
        portal.invokeFactory('Folder', 'f2')
        f1 = portal.f1
        f2 = portal.f2
        f1.invokeFactory('Document', 'f1d')
        f2.invokeFactory('Document', 'f2d')
        f1d = f1.f1d
        
        f1d.setText('"relativeref":../f2/f2d"', mimetype='text/structured')
        uid = f1d.UID()
        pl.retrieving.retrieveObject(f1d)
        
        db_cont = pl.database.queryLinks(object=[uid])
        self.assertEquals(1, len(db_cont))
        self.assertEqual(portal.absolute_url() + "/f2/f2d",
                         db_cont[0].url)

    def test_urlrecord(self):
        from gocept.linkchecker.utils import urlrecord

        components = ('scheme', 'netloc', 'path', 'parameters', 'query', 'fragment')
        urls = {
            'http://www.gocept.com':
            ['http', 'www.gocept.com', '', '', '', ''],
            'https://www.gocept.com/':
            ['https', 'www.gocept.com', '/', '', '', ''],
            'ftp://user:password@ftp.example.com/pub/barbaz':
            ['ftp', 'user:password@ftp.example.com', '/pub/barbaz', '', '', ''],
            'http://www.example.com:8080/myProject?rot=schwarz&plus=minus#muahaha':
            ['http', 'www.example.com:8080', '/myProject', '', 'rot=schwarz&plus=minus', 'muahaha'],
            '//www.example.com:8080/myProject?rot=schwarz&plus=minus#muahaha':
            ['', 'www.example.com:8080', '/myProject', '', 'rot=schwarz&plus=minus', 'muahaha'],
            'www.example.com/otherProject?rot=schwarz&plus=minus#muahaha':
            ['', '', 'www.example.com/otherProject', '', 'rot=schwarz&plus=minus', 'muahaha'],
            '../myProject?rot=schwarz&plus=minus#muahaha':
            ['', '', '../myProject', '', 'rot=schwarz&plus=minus', 'muahaha'],
            }

        for url, url_ in urls.iteritems():
            url_rec = urlrecord(url)
            url_list = [getattr(url_rec, c, '') for c in components]
            self.assertEqual(url_, url_list)
            self.assertEqual(url, str(urlrecord(url)))

    def test_resolverelative(self):
        from gocept.linkchecker.utils import resolveRelativeLink

        self.loginAsPortalOwner()
        portal = self.portal
        pl = getToolByName(portal, 'portal_linkchecker')
	pl.database.defaultURLPrefix = portal.absolute_url()

        portal.invokeFactory('Folder', 'folder')
        portal.folder.invokeFactory('Document', 'doc')
        portal_id = portal.getId()

        # Something that isn't a URL in the first place is not guaranteed to be
        # handled in a sensible way. For example, this will break things:
        #'something really/weird: which is not @ URL#...'
        urls = {
            # A protocol that should not be touched:
            'mailto:test@example.com': 'mailto:test@example.com',
            # Simple examples of all our protocols:
            'http://www.gocept.com': 'http://www.gocept.com/',
            'https://www.gocept.com': 'https://www.gocept.com/',
            'ftp://ftp.gocept.com': 'ftp://ftp.gocept.com/',
            # Trailing slash without path will be kept, none added.
            'http://www.gocept.com/': 'http://www.gocept.com/',
            # Using a path component:
            'http://www.faqs.org/rfcs/rfc2396.html':
            'http://www.faqs.org/rfcs/rfc2396.html',
            # Trailing slash after a path will be kept, none added.
            'http://www.faqs.org/rfcs/': 'http://www.faqs.org/rfcs/',
            # Using a query:
            'http://www.google.com/search?q=foobar&start=0':
            'http://www.google.com/search?q=foobar&start=0',
            # Omitting just the scheme:
            '//www.google.com/search?q=foobar&start=0':
            'http://www.google.com/search?q=foobar&start=0',
            # Also omitting the host:
            '/search?q=foobar&start=0':
            'http://nohost/search?q=foobar&start=0',
            # a relative URL with regular path elements only:
            'search?q=foobar&start=0':
            'http://nohost/$PORTAL/folder/search?q=foobar&start=0',
            # a relative URL with leading ..:
            '../search?q=foobar&start=0':
            'http://nohost/$PORTAL/search?q=foobar&start=0',
            # a relative URL with leading .. and no-ops:
            './../search?q=foobar&start=0':
            'http://nohost/$PORTAL/search?q=foobar&start=0',
            # a relative URL with a trailing slash:
            './': 'http://nohost/$PORTAL/folder/',
            # a relative URL without a trailing slash:
            '.': 'http://nohost/$PORTAL/folder/',
            # a relative URL with too many leading ..:
            '../../..': 'http://nohost/',
            }

        for before, expected in urls.iteritems():
            after = resolveRelativeLink(before, portal.folder.doc)
            expected = expected.replace('$PORTAL', portal_id)
            self.assertEqual(expected, after)

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(LinkCheckerTest))
    return suite
