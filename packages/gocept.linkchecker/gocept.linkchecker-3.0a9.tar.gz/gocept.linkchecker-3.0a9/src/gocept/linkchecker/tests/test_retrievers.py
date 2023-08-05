# Copyright (c) 2004 gocept gmbh & co. kg
# See also LICENSE.txt
# 

import unittest

from Products.Archetypes.tests.common import *
from Products.Archetypes.tests.utils import *

from Products.Archetypes.tests.test_sitepolicy import makeContent
from Products.CMFCore.utils import getToolByName

import zope.lifecycleevent
import gocept.linkchecker.retrievemanager
from gocept.linkchecker import retrievers

from gocept.linkchecker.tests.base import LinkCheckerTestCase


class LinkCheckerTest(LinkCheckerTestCase):

    def test_event_retriever(self):
        self.loginAsPortalOwner()
        links = ["http://www.asdf.org", "http://www.bauhaus.de",
                 "ftp://www.goodbye.de", "http://www.google.de/img.png"]

        text = " ".join( [ """"asdf":%s\n""" % x for x in links ])
        lc = getToolByName(self.portal, 'portal_linkchecker')

        url = "http://asdf.org"
        event = makeContent(self.portal, portal_type="Event", id="asdf")
        event.edit(event_url=url)
        event.setText(text)

        retriever = retrievers.Event(event)
        links = retriever.retrieveLinks()

        self.assertEqual(len(links), 5)
        self.assertEqual(links[0], url)

        # The general AT retriever doesn't find this URL
        links = retrievers.ATGeneral(event).retrieveLinks()
        self.assertEqual(links[0], "http://www.google.de/img.png")
        self.assertEqual(len(links), 4)

        # The retriever can also update the URL
        retriever.updateLink(url, 'http://foobar.org')
        self.assertEquals(event.event_url(), 'http://foobar.org')

        # If the URL to replace does not match, it doesn't change the URL of
        # the event:
        retriever.updateLink('blubb', 'http://quux.org')
        self.assertEquals(event.event_url(), 'http://foobar.org')

    def test_link_retriever(self):
        self.loginAsPortalOwner()
        lc = getToolByName(self.portal, 'portal_linkchecker')

        url = "http://www.asdf.org/asdf?asdf"
        ob = makeContent(self.portal, portal_type="Link", id="asdf")
        ob.edit(url)

        retriever = retrievers.Link(ob)
        links = retriever.retrieveLinks()

        self.assertEqual(len(links), 1)
        self.assertEqual(links[0], url)

        # The retriever can also update the URL
        retriever.updateLink(url, 'http://www.foobar.org')
        self.assertEquals(ob.getRemoteUrl(), 'http://www.foobar.org')

        # If the URL doesn't match, the link won't be updated
        retriever.updateLink(url, 'http://www.quux.org')
        self.assertEquals(ob.getRemoteUrl(), 'http://www.foobar.org')


    def test_document_html_retriever(self):
        self.loginAsPortalOwner()
        links = ["http://www.asdf.org", "http://www.bauhaus.de",
                 "ftp://www.goodbye.de", "http://www.google.de/img.png"]
        text = " ".join( [ """<a href="%s">asdf</a>""" % x for x in links[:-1] ])
        text += """<img src="%s"/>""" % links[-1]

        lc = getToolByName(self.portal, 'portal_linkchecker')

        url = "http://www.asdf.org/asdf?asdf"
        ob = makeContent(self.portal, portal_type="Document", id="asdf")
        ob.setText(text)

        retriever = retrievers.ATGeneral(ob)
        links_ob = retriever.retrieveLinks()
        self.assertEqualLinks(links, links_ob)

        # The retriever can also update URLs
        retriever.updateLink('http://www.asdf.org', 'http://foo.org')
        self.assertEquals(ob.getText(),
            """<a href="http://foo.org">asdf</a> """
            """<a href="http://www.bauhaus.de">asdf</a> """
            """<a href="ftp://www.goodbye.de">asdf</a>"""
            """<img src="http://www.google.de/img.png" />""")

        # As this goes through various decoding cycles, we need to be careful
        # about encodings:
        ob.setText(u'<a href="asdf.org">\xf6</a>')
        retriever.updateLink('asdf.org', 'bsdf.org')
        # AT converts to utf-8 encoded byte strings internally
        self.assertEquals(ob.getText().decode('utf-8'),
                          u'<a href="bsdf.org">\xf6</a>')

    def test_document_stx_retriever(self):
        self.loginAsPortalOwner()
        links = ["http://www.asdf.org", "http://www.bauhaus.de",
                 "ftp://www.goodbye.de", "http://www.google.de/img.png"]

        text = " ".join( [ """"asdf":%s\n""" % x for x in links ])

        lc = getToolByName(self.portal, 'portal_linkchecker')

        url = "http://www.asdf.org/asdf?asdf"
        ob = makeContent(self.portal, portal_type="Document", id="asdf")
        ob.setText(text, mimetype='text/structured')

        # RichTextRetriever should work just as well.
        links_ob = retrievers.ATGeneral(ob).retrieveLinks()
        self.assertEqualLinks(links, links_ob)

    def assertEqualLinks(self, links, links_ob):
        self.assertEqual(len(links), len(links_ob))
        for x in links_ob:
            self.assert_(x in links)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(LinkCheckerTest))
    return suite
