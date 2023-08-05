# Copyright (c) 2004 gocept gmbh & co. kg
# See also LICENSE.txt
# 

import unittest

import time

from Products.Archetypes.tests.common import *
from Products.Archetypes.tests.utils import *

import Acquisition

from gocept.linkchecker.tests.base import LinkCheckerTestCase

from Products.CMFCore.utils import getToolByName

class Dummy(Acquisition.Implicit):
    
    started = False
    
    def start(self):
        """dummy method getting called by portal catalog"""
        self.started = True
        

class LinkCheckerReportTest(LinkCheckerTestCase):

    def test_ManagementOverview(self):
        lc = getToolByName(self.portal, 'portal_linkchecker')
        status = lc.reports.ManagementOverview()
    
        self.assertEquals(status.totalLinks, 0)
        self.assertEquals(status.links['red'], 0)
        self.assertEquals(status.links['grey'], 0)
        self.assertEquals(status.links['green'], 0)
        self.assertEquals(status.links['orange'], 0)
        self.assertEquals(status.linksPct['red'], 0)
        self.assertEquals(status.linksPct['grey'], 0)
        self.assertEquals(status.linksPct['green'], 0)
        self.assertEquals(status.linksPct['orange'], 0)
        

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(LinkCheckerReportTest))
    return suite
