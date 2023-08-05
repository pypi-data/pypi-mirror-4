# Copyright (c) 2005 gocept gmbh & co. kg
# See also LICENSE.txt
# 
"""CMF link checker tool - link retriever functions"""

import Products.ATContentTypes.content.event
import Products.ATContentTypes.content.link
import gocept.linkchecker.interfaces
import gocept.linkchecker.utils
import zope.component
import zope.interface


class Link(object):
    """Retriever for ATCT Link objects."""

    zope.component.adapts(Products.ATContentTypes.content.link.ATLink)
    zope.interface.implements(gocept.linkchecker.interfaces.IRetriever)

    def __init__(self, context):
        self.context = context

    def retrieveLinks(self):
        """Finds all links from the object and return them."""
        return [self.context.getRemoteUrl()]

    def updateLink(self, oldurl, newurl):
        """Replace all occurances of <oldurl> on object with <newurl>."""
        if self.context.getRemoteUrl() == oldurl:
            self.context.setRemoteUrl(newurl)


class Event(object):
    """Retriever for ATCT Event objects"""

    zope.component.adapts(Products.ATContentTypes.content.event.ATEvent)
    zope.interface.implements(gocept.linkchecker.interfaces.IRetriever)

    def __init__(self, context):
        self.context = context

    def retrieveLinks(self):
        """Finds all links from the object and return them."""
        links = [self.context.event_url()]
        for link in gocept.linkchecker.utils.retrieveAllRichTextFields(
                self.context):
            links.append(link)
        return links

    def updateLink(self, oldurl, newurl):
        """Replace all occurances of <oldurl> on object with <newurl>."""
        if self.context.event_url() == oldurl:
            self.context.setEventUrl(newurl)
        gocept.linkchecker.utils.updateAllRichTextFields(
            oldurl, newurl, self.context)


class ATGeneral(object):
    """General retriever for Archetypes that extracts URLs from (rich) text
    fields.
    """

    zope.component.adapts(Products.Archetypes.atapi.BaseContent)
    zope.interface.implements(gocept.linkchecker.interfaces.IRetriever)

    def __init__(self, context):
        self.context = context

    def retrieveLinks(self):
        """Finds all links from the object and return them."""
        return gocept.linkchecker.utils.retrieveAllRichTextFields(self.context)

    def updateLink(self, oldurl, newurl):
        """Replace all occurances of <oldurl> on object with <newurl>."""
        gocept.linkchecker.utils.updateAllRichTextFields(
            oldurl, newurl, self.context)
