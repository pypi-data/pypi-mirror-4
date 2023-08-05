# Copyright (c) 2003-2005 gocept gmbh & co. kg
# See also LICENSE.txt
"""CMF link checker tool"""

# Python imports
import time
from types import StringTypes
from warnings import warn
import zope.interface

# Global Zope imports
from AccessControl import getSecurityManager, ClassSecurityInfo
from DateTime import DateTime
from OFS.Folder import Folder
from Globals import InitializeClass
from Acquisition import aq_base

# CMF/Plone imports
from Products.CMFCore.utils import UniqueObject, getToolByName
from Products.CMFCore.permissions import ManagePortal
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.CMFCore.ActionProviderBase import ActionProviderBase
from Products.CMFCore.ActionInformation import ActionInformation
from Products.CMFCore.Expression import Expression

from Products.Archetypes.interfaces.referenceable import IReferenceable

# Sibling imports
from gocept.linkchecker.interfaces import ILinkManager
from gocept.linkchecker.utils import resolveRelativeLink
from gocept.linkchecker import permissions, shorturls

LMS_REGISTRATION = "http://www.gocept.com/portal_lms_registration"


class LinkCheckerTool(UniqueObject, Folder):
    """A link checker tool. Encapsulating mechanisms for finding links in the
       site, testing their availability and notifying their owners."""

    zope.interface.implements(ILinkManager)

    id = 'portal_linkchecker'
    meta_type = 'CMF Linkchecker Tool'

    security = ClassSecurityInfo()

    plone_tool = 1

    manage_options = ( ({'label' : 'Overview', 'action' : 'manage_overview'},) +
                        Folder.manage_options )

    # Provide means to avoid retrieving/indexing/... events to trigger while
    # we're not set up correctly, yet.
    active = False

    #
    # ZMI methods
    #
    security.declareProtected(ManagePortal, 'manage_overview')
    manage_overview = PageTemplateFile('www/explainLinkcheckerTool', globals(),
                                        __name__='manage_overview')

    def manage_afterAdd(self, item, container):
        LinkCheckerTool.inheritedAttribute('manage_afterAdd')(self, item,
                                                              container)
        object_ids = self.objectIds()

        if 'retrieving' not in object_ids:
            self.manage_addProduct["gocept.linkchecker"].\
                    manage_addRetrieveManager('retrieving')
        if 'database' not in object_ids:
            self.manage_addProduct["gocept.linkchecker"].\
                    manage_addLinkDatabase('database')
        if 'reports' not in object_ids:
            self.manage_addProduct["gocept.linkchecker"].\
                    manage_addBaseReports('reports')

        self.active = True

    ##############
    # ILinkManager

    security.declarePublic("shortURL")
    def shortURL(self, url, target=50):
        """Context aware wrapper for creating a shortened URL"""
        base = self.database.defaultURLPrefix
        return shorturls.shortURL(url, target, base)

    security.declarePublic("isManaged")
    def isManaged(self, object):
        """Tells if the object is managed by the link manager."""
        return self.retrieving.supportsRetrieving(object)

    security.declarePublic('resolveRelativeLink')
    def resolveRelativeLink(self, url, context):
        return resolveRelativeLink(url, context)

    def isUserAllowed(self):
        """returns whether the user is allowed to use Link Management services
        """
        security = getSecurityManager()
        portal = getToolByName(self, 'portal_url').getPortalObject()
        return security.checkPermission(permissions.USE_LINK_MANAGEMENT,
                                        portal)

    ######
    # misc

    security.declarePublic("registrationURL")
    def registrationURL(self):
        """Return the URL for registering with the gocept lms."""
        # XXX not sure which of REQUEST.URL or REQUEST.ACTUAL_URL is best here
        return_url = "%s#form_client_id" % self.REQUEST.URL 
        portal = getToolByName(self, 'portal_url').getPortalObject()
        callback_url = portal.portal_linkchecker.database.absolute_url()

        return "%s?callback_url=%s&return_url=%s" % (LMS_REGISTRATION,
                                                     callback_url, return_url)

    security.declareProtected(ManagePortal, 'getInfoFrameURL')
    def getInfoFrameURL(self):
        """Returns the URL received from the LMS or an empty string."""
        return self.database.getInfoFrameURL()


InitializeClass(LinkCheckerTool)
