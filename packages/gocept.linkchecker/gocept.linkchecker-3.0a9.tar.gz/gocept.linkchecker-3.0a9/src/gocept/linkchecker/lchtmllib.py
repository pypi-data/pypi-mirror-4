##############################################################################
#
# Copyright (c) 2003 gocept gmbh & co. kg. All rights reserved.
#
# See also LICENSE.txt
#
##############################################################################
"""Customized HTML parser to find images in an imglist (similar to anchorlist)
"""

from htmllib import HTMLParser

class LCHTMLParser(HTMLParser):

    imglist = []

    def do_img(self, attrs):
        for attrname, value in attrs:
            if attrname == "src":
                if not self.imglist:
                    self.imglist = []
                self.imglist.append(value)
