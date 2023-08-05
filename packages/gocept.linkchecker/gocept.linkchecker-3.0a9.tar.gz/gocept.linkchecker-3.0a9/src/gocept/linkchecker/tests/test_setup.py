# vim:fileencoding=utf-8
# Copyright (c) 2008 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import unittest
from gocept.linkchecker.tests.base import LinkCheckerTestCase
from Products.Five.testbrowser import Browser

class TestSetup(LinkCheckerTestCase):

    def test_portal_tool(self):
        self.assert_('portal_linkchecker' in self.portal.objectIds())

    def test_actions(self):
        # Ensure that all actions were registered.
        b = Browser()
        b.open(self.portal.absolute_url()+'/login')
        b.getControl(name='__ac_name').value = self.portal_owner
        b.getControl(name='__ac_password').value = self.default_password
        b.getControl(name='submit').click()
        b.open(self.portal.absolute_url())
        self.assert_(b.getLink('Link management'))
        self.assert_(b.getLink('My links'))
        self.assert_(b.getLink('Links'))


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestSetup))
    return suite
