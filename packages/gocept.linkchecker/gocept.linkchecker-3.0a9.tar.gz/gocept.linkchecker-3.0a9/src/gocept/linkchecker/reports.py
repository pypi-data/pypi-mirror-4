# Copyright (c) 2003-2005 gocept gmbh & co. kg
# See also LICENSE.txt
# 
"""CMF link checker tool - basic reports
"""

# Python imports
import time

# Zope imports
import zope.interface
from OFS.SimpleItem import SimpleItem
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo, getSecurityManager
from DateTime import DateTime

# CMF/Plone imports
from Products.CMFCore import permissions
from Products.CMFCore.utils import getToolByName

from gocept.linkchecker.interfaces import IBaseReports
from gocept.linkchecker import permissions


def manage_addBaseReports(container, id):
    """Add basic reports to a link manager."""
    container._setObject(id, BaseReports(id))


class BaseReports(SimpleItem):
    """Supplement functions for various basic reports."""

    zope.interface.implements(IBaseReports)
    security = ClassSecurityInfo()

    def _filter_report(self, member, report):
        """Returns a filtered report, which may be None.
        """
        report_states = member.getProperty('lc_notify_details', [])
        if not isinstance(report_states, (list, tuple)):
            return None

        for state in report.keys():
            if state not in report_states:
                del report[state]

        changes_only = member.getProperty('lc_notify_changes_only', False)
        if changes_only:
            last_report = member.getProperty('lc_notify_last_notification',
                                             DateTime())
            for state, links in report.items():
                # remove already reported links (did not change)
                links = [link for link in links
                         if link.lastupdate >= last_report]
                if links:
                    report[state] = links
                    for link in links:
                        if link.laststate in report:
                            # add some extra information
                            report[link.laststate].append(link)
                else:
                    del report[state]
            if not report:
                return None

        return report

    security.declarePublic('GroupedLinksForAuthenticatedMember')
    def GroupedLinksForAuthenticatedMember(self):
        """Returns a list of links aggregated by state for the current user.
        
           The list only features catalog brains from the database.
        """
        user = getSecurityManager().getUser().getId()
        return self.getGroupedLinksFor(user)
    
    security.declareProtected(permissions.ManagePortal,
                              'getGroupedLinksFor')
    def getGroupedLinksFor(self, user_id):

        catalog = getToolByName(self, 'portal_catalog')
        lc = getToolByName(self, 'portal_linkchecker')

        # Find all objects this user is responsible for
        docs = catalog(Creator=user_id, Language='all')
        uids = [ x.UID for x in docs ]
        uids = filter(None, uids)
        links = lc.database.queryLinks(object=uids)

        groups = {'red': [], 'blue': [], 'orange': [], 'grey': [], 'green': []}
        for link in links:
                groups[link.state].append(link)
        return groups


    security.declareProtected(permissions.ManagePortal, "LinkStateInfo")
    def LinkStateInfo(self, link):
        # Resolve a link brain object into something more useful for the
        # LinksInState report
        pms = getToolByName(self, 'portal_membership')
        link = link.getObject()
        item = {}
        item["url"] = link.url
        item["reason"] = link.reason
        item["lastcheck"] = link.lastcheck
        item["id"] = link.getId
        item["link"] = link.link
        item["document"] = link.getObject()
        item["object"] = link.object
        item["owner_mail"] = ""
        item["owner"] = item["document"].Creator()
        try:
            member = pms.getMemberById(creator)
            item["owner_mail"] = member.getProperty("email")
            item["owner"] = member.getProperty("fullname", item["owner"])
        except Exception:
            pass
        return item

    security.declareProtected(permissions.ManagePortal, "LinksInState")
    def LinksInState(self, state):
        """Returns a list of links in the given state."""
        lc = getToolByName(self, 'portal_linkchecker')
        return lc.database.queryLinks(state=[state], sort_on="url")
    
    security.declareProtected(permissions.ManagePortal,
                              'ManagementOverview')
    def ManagementOverview(self):
        """Returns a comprehensive management overview over the complete site
        """
        return ManagementReport(self)
        


InitializeClass(BaseReports)


class ManagementReport:

    __allow_access_to_unprotected_subobjects__ = 1

    states = [
        ('green', 'Green'),
        ('orange', 'Orange'),
        ('red', 'Red'),
        ('blue', 'Blue'),
        ('grey', 'Grey'),
    ]

    def __init__(self, context):
        self._context = context
        self._generate_data()

    def _generate_data(self):
        lc = getToolByName(self._context, 'portal_linkchecker')
   
        self.links = {}
        for state in ['red', 'grey', 'green', 'orange', 'blue']:
            self.links[state] = len(lc.database.queryLinks(state=[state]))

        self.totalLinks = sum(self.links.values())

        if self.totalLinks:
            self.linksPct = {}
            for state, count in self.links.items():
                self.linksPct[state] = float(count) / self.totalLinks * 100
        else:
            # All zeros
            self.linksPct = self.links
