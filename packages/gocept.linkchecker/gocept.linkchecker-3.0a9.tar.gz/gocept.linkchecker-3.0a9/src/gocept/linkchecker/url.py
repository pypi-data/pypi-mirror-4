# Copyright (c) 2003-2005 gocept gmbh & co. kg
# See also LICENSE.txt
# 
"""CMF link checker tool - url object
"""

# Zope imports
from DateTime import DateTime
from OFS.SimpleItem import SimpleItem
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

# CMF/Plone imports
from Products.CMFCore.utils import getToolByName

# Sibling imports
import gocept.linkchecker.interfaces
import gocept.linkchecker.utils


class URL(SimpleItem):
    """URL status information"""

    meta_type = "URL"

    __implements__ = (gocept.linkchecker.interfaces.IURL,)
    # XXX make accessor functions
    __allow_access_to_unprotected_subobjects__ = 1

    url = None
    lastcheck = None
    lastupdate = None
    laststate = "grey"
    state = "grey"
    reason = ""
    registered = False

    manage_options = ({'label': 'Info', 'action':'manage_info'},) + \
                     SimpleItem.manage_options

    manage_info = PageTemplateFile('www/url', globals(), __name__='manage_info')

    def __init__(self, url):
        self.id = gocept.linkchecker.utils.hash_url(url)
        self.url = url

    def getLinks(self):
        lc = getToolByName(self, "portal_linkchecker")
        return lc.database.getLinksForURL(self.url)

    def updateStatus(self, state, reason):
        assert state in ['red', 'green', 'orange', 'grey', 'blue'], \
            "Invalid state %s" % state
        self.reason = reason
        now = DateTime()
        self.lastcheck = now
        if state != self.state:
            self.laststate = self.state
            self.state = state 
            self.lastupdate = now
        self.index()
        # Reindex link objects to update their status caches
        for link in self.getLinks():
            link.index()

    # Python/Zope helper functions
    def __repr__(self):
        return "<URL %s (%s)>" % (self.url, self.state)

    def _p_resolveConflict(self, oldState, savedState, newState):
        # This happens if the LMS starts talking to us and we do crawling
        # and the site is busy in general.
        # However, we are only interested in the news information we get,
        # so we can happily do something simple here.
        return newState

    # Catalog support
    def manage_afterAdd(self, container, object):
        self.index()

    def manage_beforeDelete(self, item, container):
        return
        self.unindex()

    def index(self):
        path = '/'.join(self.getPhysicalPath())
        self.url_catalog.catalog_object(self, path)

    def unindex(self):
        path = '/'.join(self.getPhysicalPath())
        self.url_catalog.uncatalog_object(path)
