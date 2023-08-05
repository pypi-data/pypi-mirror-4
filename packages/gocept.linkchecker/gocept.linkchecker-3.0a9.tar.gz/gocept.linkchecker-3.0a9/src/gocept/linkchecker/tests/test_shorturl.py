# Copyright (c) 2003-2005 gocept gmbh & co. kg
# See also LICENSE.txt
# 

"""ShortURL tests"""



import unittest
from Testing import ZopeTestCase

from unittest import TestSuite, TestCase, makeSuite, main
from gocept.linkchecker.shorturls import shortURL


class ShortURLTest(TestCase):

    def testNormal(self):
        url = "http://www.gocept.com"
        self.assertEqual(shortURL(url), url)

        url = "http://www.gocept.com/test"
        self.assertEqual(shortURL(url, len(url)), url)

        url = "http://www.gocept.com/test/test1/test2;parameter?query=1#fragment"
        self.assertEqual(shortURL(url, len(url)), url)

    def testPathFolding(self):

        url = "http://www.gocept.com/angebot/opensource/gocept.linkchecker/revision1.3"
        self.assertEqual(shortURL(url), "http://www.gocept.com/angebot/.../revision1.3")
        self.assertEqual(shortURL(url, 40), "http://www.gocept.com/.../revision1.3")

    def testPriorityFolding(self):

        url = "http://www.gocept.com/angebot/opensource/gocept.linkchecker/revision1.3;asdf?query=1#fragment"
        
        self.assertEqual(shortURL(url, 89), 
              "http://www.gocept.com/angebot/opensource/gocept.linkchecker/revision1.3;asdf?query=1#...")

        self.assertEqual(shortURL(url, 84), 
              "http://www.gocept.com/angebot/opensource/gocept.linkchecker/revision1.3;asdf?...#...")
        
        self.assertEqual(shortURL(url, 60), 
              "http://www.gocept.com/angebot/.../revision1.3;...?...#...")


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(ShortURLTest))
    return suite
