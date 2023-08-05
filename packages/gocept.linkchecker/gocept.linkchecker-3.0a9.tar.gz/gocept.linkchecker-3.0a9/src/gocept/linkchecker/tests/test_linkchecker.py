# Copyright (c) 2004 gocept gmbh & co. kg
# See also LICENSE.txt
# 

import Acquisition
from Products.CMFCore.utils import getToolByName
from Products.Archetypes.tests.test_sitepolicy import makeContent
from gocept.linkchecker.tests.base import LinkCheckerTestCase
from gocept.linkchecker.interfaces import ILink

import time
import unittest
import zope.lifecycleevent


class LinkCheckerTest(LinkCheckerTestCase):


    def test_link_registration(self):
        self.loginAsPortalOwner()
        doc = makeContent(self.portal, portal_type="Document", id="asdf")

        lc = getToolByName(self.portal, 'portal_linkchecker')
        lc['database'].offline = True
        links = ["http://www.gocept.com", 
                 "http://www.asfdhasdkjfhasdkjhfkjsda.org", 
                 "http://www.zope.org", "http://www.microsoft.com"]
        info = lc.database.registerLinks(links, doc)

        # Check for the links the object was registered for
        doc_links = lc.database.getLinksForObject(doc)
        self.assertEqual(len(links), len(doc_links))

        for l in doc_links:
            self.failUnless(l.link in links)

    def test_crawling(self):
        self.loginAsPortalOwner()
        lc = getToolByName(self.portal, 'portal_linkchecker')
        lc['database'].offline = True
        
        links = ["http://www.google.de/", "http://www.gocept.com/",
            "http://www.arcor.de/", "http://www.gocept.com/"]
        docs = []
        
        for x in links:
            id = self.portal.generateUniqueId()
            doc = makeContent(self.portal, portal_type="Document", id=id)
            doc.edit('html', '<a href="%s">asdf</a>' % x)
            docs.append(doc)

        lc.retrieving.retrieveSite()

        # XXX 25 is an arbitrary amount as the stock Plone site already
        # contains an unknown number.
        self.assertEqual(lc.database.getLinkCount(), 25)

        # However, the three URLs provided above are now known and have
        # associated links:
        google = lc.database.getLinksForURL('http://www.google.de/')
        self.assertEquals(len(google), 1)
        gocept = lc.database.getLinksForURL('http://www.gocept.com/')
        self.assertEquals(len(gocept), 2)
        arcor = lc.database.getLinksForURL('http://www.arcor.de/')
        self.assertEquals(len(arcor), 1)

        # Each of the documents that we created has a link associated now
        # which is in the list of the URLs above.
        for doc in docs:
            l = lc.database.getLinksForObject(doc)
            self.assertEqual(len(l), 1)
            self.failUnless(ILink.providedBy(l[0]))
            self.failUnless(l[0].url() in links)

    def test_deletion(self):
        self.loginAsPortalOwner()
        lc = getToolByName(self.portal, 'portal_linkchecker')
        lc['database'].offline = True
        lc.retrieving.retrieveSite()
        # XXX 21 is an arbitrary amount as the stock Plone site already
        # contains an unknown number.
        self.assertEqual(21, lc.database.getLinkCount())

        # Now we delete an object and re-crawl the site. This should cause the
        # number of links to drop.
        self.portal.manage_delObjects(['front-page'])
        self.assertEqual(0, lc.database.getLinkCount())

    def test_crawl_offline(self):
        self.loginAsPortalOwner()
        lc = getToolByName(self.portal, 'portal_linkchecker')
        lc.database.configure(clientid='does-not-exist')

    def test_sync_failing(self):
        self.loginAsPortalOwner()
        lc = getToolByName(self.portal, 'portal_linkchecker')
        self.assertRaises(AttributeError, lc.database.sync)

    def test_byobject(self):
        self.loginAsPortalOwner()
        lc = getToolByName(self.portal, 'portal_linkchecker')
        db = lc.database
        doc = makeContent(self.portal, portal_type="Document", id="asdf")
        doc.setText('''"<a href='bla/fasel'>foo</a>
                    <a href='http://www.gocept.com'>gocept</a>''')
        
        lc.retrieving.retrieveObject(doc)

        links = db.getLinksForObject(doc)
        self.assertEquals(2, len(links))
     
    def test_atsupport(self):
        self.loginAsPortalOwner()
        portal = self.portal
        lc = getToolByName(portal, 'portal_linkchecker')
        db = lc.database
        portal.invokeFactory('Document', 'd1')
        d1 = portal.d1
        
        d1.setText('<a href="http://www.gocept.com">bla</a>')
        zope.event.notify(zope.lifecycleevent.ObjectModifiedEvent(d1))
        links = db.getLinksForObject(d1)
        self.assertEquals(1, len(links))

        d1.setText('foo')
        zope.event.notify(zope.lifecycleevent.ObjectModifiedEvent(d1))
        links = db.getLinksForObject(d1)
        self.assertEquals(0, len(links))


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(LinkCheckerTest))
    return suite
