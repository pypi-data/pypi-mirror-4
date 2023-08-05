# Copyright (c) 2003-2009 gocept gmbh & co. kg
# See also LICENSE.txt
"""gocept.linkchecker - link information object"""

from DateTime import DateTime
from OFS.SimpleItem import SimpleItem
from Products.CMFCore.utils import getToolByName
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
import gocept.linkchecker.interfaces
import gocept.linkchecker.utils
import zope.interface 


class Link(SimpleItem):
    """A link as used from an object."""

    meta_type = "Link"

    zope.interface.implements(gocept.linkchecker.interfaces.ILink)

    __allow_access_to_unprotected_subobjects__ = 1

    manage_options = ({'label': 'Info', 'action':'manage_info'},) + \
                     SimpleItem.manage_options
    manage_info = PageTemplateFile('www/link', globals(), __name__='manage_info')

    def __init__(self, link, id, object):
        self.object = object
        self.link = link
        self.id = id

    def __setstate__(self, state):
        for key in ['url', 'state', 'lastcheck', 'reason']:
            if 'url' in state:
                del state['url']
        SimpleItem.__setstate__(self, state)

    # gocept.linkchecker.interfaces.ILink
    def getURL(self):
        """Return the URL object this link refers to."""
        lc = getToolByName(self, "portal_linkchecker")
        url = self.url()
        res = lc.database.queryURLs(url=url)
        if not res:
            # Ensure the URL exists
            raise ValueError("Could not find URL %s." % url)
        return res[0].getObject()

    def getObject(self):
        """Return a reference to the object."""
        references = getToolByName(self, "reference_catalog")
        return references.lookupObject(self.object)

    # Python/Zope helpers 
    def __repr__(self):
        return "<Link %s at %s>" % (self.link, self.object)

    # Catalog support
    def manage_afterAdd(self, container, object):
        self.index()

    def manage_beforeDelete(self, item, container):
        self.unindex()

    def index(self):
        if self.getObject() is None:
            self.getParentNode().manage_delObjects([self.id])
            return 
        try:
            url = self.getURL()
        except ValueError:
            # Make sure the URL object exists when we index ourselves.
            url = gocept.linkchecker.url.URL(self.url())
            db = self.getLinkCheckerDatabase()
            if url.id not in db.objectIds():
                db._setObject(url.id, url)
            url = db[url.id]
        path = '/'.join(self.getPhysicalPath())
        self.link_catalog.catalog_object(self, path)

    def unindex(self):
        path = '/'.join(self.getPhysicalPath())
        try:
            catalog = self.link_catalog
        except AttributeError:
            # This is a special case to handle very large databases: empty or
            # delete the catalog then delete stuff
            return
        catalog.uncatalog_object(path)

    def url(self):
        return gocept.linkchecker.utils.resolveRelativeLink(
            self.link, self.getObject())

    def state(self):
        return self.getURL().state

    def reason(self):
        return self.getURL().reason

    def lastcheck(self):
        return self.getURL().lastcheck
