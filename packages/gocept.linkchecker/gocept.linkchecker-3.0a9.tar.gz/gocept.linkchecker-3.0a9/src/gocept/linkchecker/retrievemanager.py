# Copyright (c) 2003-2005 gocept gmbh & co. kg
# See also LICENSE.txt
# 
"""Retrieve manager."""

# Zope imports
import transaction
import zope.interface
import gocept.linkchecker.log as log
import zope.lifecycleevent.interfaces
import zope.app.container
import zope.component
from AccessControl import ClassSecurityInfo, getSecurityManager, Unauthorized
from Globals import InitializeClass, PersistentMapping
from OFS.SimpleItem import SimpleItem
from zope.app.component.hooks import getSite
import zope.app.container.interfaces
import Products.Archetypes.interfaces

# CMF/Plone imports
from Products.CMFCore.permissions import ManagePortal
from Products.CMFCore.permissions import ModifyPortalContent
from Products.CMFCore.utils import getToolByName

import gocept.linkchecker.interfaces

def manage_addRetrieveManager(container, id):
    """Add a new retriever manager to a link manager."""
    container._setObject(id, RetrieveManager(id))


class RetrieveManager(SimpleItem):
    """Local registry that manages the mapping between portal_type and 
       specific retrievers for a single plone instance and allows to trigger
       retrieving for an object or the whole site.
    """

    zope.interface.implements(gocept.linkchecker.interfaces.IRetrieveManager)
    security = ClassSecurityInfo()

    def __init__(self, id):
        self.id = id

    ##################
    # IRetrieveManager

    security.declarePublic('retrieveObject')
    def retrieveObject(self, object, online=True):
        # Check for ModifyPortalContent-Permission on context object.
        # This is dangerous, but I think I know what I'm doing.
        sm = getSecurityManager()
        if not sm.checkPermission(ModifyPortalContent, object):
            return
        if (not
            Products.Archetypes.interfaces.IReferenceable.providedBy(object)):
            return
        database = self.getParentNode().database
        database.unregisterObject(object)
        retriever = gocept.linkchecker.interfaces.IRetriever(object, None)
        if retriever is not None:
            links = retriever.retrieveLinks()
            database.registerLinks(links, object, online)

    security.declarePublic('updateObject')
    def updateLink(self, old_link, new_link, object):
        # Check for ModifyPortalContent-Permission on context object.
        # This is dangerous, but I think I know what I'm doing.
        sm = getSecurityManager()
        if not sm.checkPermission(ModifyPortalContent, object):
            raise Unauthorized, "You can't update links for this object."
        retriever = gocept.linkchecker.interfaces.IRetriever(object, None)
        if retriever is not None:
            retriever.updateLink(old_link, new_link)
        self.retrieveObject(object)

    security.declareProtected(ManagePortal, 'retrieveSite')
    def retrieveSite(self):
        """Retrieves the links from all objects in the site."""
        database = self.getParentNode().database
        objects = self.portal_catalog(Language='all')
        os_ = len(objects)
        i = 0
        for ob in objects:
            try:
                obj = ob.getObject()
            except Exception, e:
                # Maybe the catalog isn't up to date
                log.logger.debug("Site crawl raised an error for %s: %s" % (ob.getPath(), str(e)))
                continue
            i += 1
            log.logger.debug("Site Crawl Status %s of %s (%s)" % (i, os_, ob.getPath()))
            self.retrieveObject(obj, online=False)
            if not i % 100:
                # Memory optimization
                transaction.savepoint()

    def supportsRetrieving(self, object):
        """Tells if the object is supported for retrieving links."""
        retriever = gocept.linkchecker.interfaces.IRetriever(object, None)
        return bool(retriever)


InitializeClass(RetrieveManager)


def remove_links(event):
    object = event.object
    try:
        link_checker = getToolByName(object, 'portal_linkchecker').aq_inner
    except AttributeError:
        return
    if not link_checker.active:
        return
    link_checker.database.unregisterObject(object)


def update_links(event):
    object = event.object
    portal = getSite()
    if not portal or not hasattr(portal, 'portal_factory'):
        return
    temporary = portal.portal_factory.isTemporary(object)
    if temporary:
        # Objects that are temporary (read: portal_factory) and do not have a
        # (stable) URL (yet) do not need to be crawled: relative links will be
        # off quickly and we can't really use the UID anyway.
        return
    try:
        link_checker = getToolByName(object, 'portal_linkchecker').aq_inner
    except AttributeError:
        return
    if not link_checker.active:
        return
    link_checker.retrieving.retrieveObject(object)
