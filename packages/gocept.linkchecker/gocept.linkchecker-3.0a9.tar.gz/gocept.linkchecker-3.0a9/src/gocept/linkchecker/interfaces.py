# Copyright (c) 2003-2005 gocept gmbh & co. kg
# See also LICENSE.txt
# 
"""gocept.linkchecker interface definitions"""


from zope.interface import Interface, Attribute

from Products.Archetypes import public as atapi


class ILinkManager(Interface):

    database = Attribute("A link database implementing the "
                         "ILinkDatabase interface.")
    reports = Attribute("A report utility implementing the "
                        "IBaseReports interface.")
    retrieving = Attribute("A retrieve manager implementing the "
                           "IRetrieveManager interface.")

    def shortURL(url, target=50):
        """Context aware wrapper for creating a shortened URL"""

    def isManaged(object):
        """Tells if the object is managed by the link manager."""

    def resolveRelativeLink(url, context):
        """Resolve relative URL from context to an absolute URL.

        This is similar to the absolute_url(), but does not require an object
        and honours the prefix settings from the link management settings.
        """

    def isUserAllowed():
        """Returns whether the user is allowed to use link management
        services.

        Returns True, iff the currently logged in user is allowed to use link
            management services at all.

        This function checks whether the user has the 'Use link management functions'
        permission in the Plone root.
        """

    def getLinkManager():
        """return self"""


class IBaseReports(Interface):
    """Supplement functions for various basic reports."""

    def GroupedLinksForAuthenticatedMember():
        """Returns a list of links aggregated by state for the current user.

           The list only features catalog brains from the database.
        """

    def DocumentsInState(state):
        """Returns a list of all objects that contain links in the given state.
        """

    def LinksInState(state):
        """Returns a list of links in the given state."""

    def ManagementOverview():
        """Returns a comprehensive management overview over the complete site.
        """


class ILinkDatabase(Interface):
    """A database of links. 

       Manages the physical storage of link information.
    """

    defaultURLPrefix = Attribute("A valid URL that is used (component wise) to "
                                 "prepend incomplete links")

    def configure(defaultURLPrefix=None):
        """Set configuration values."""

    def unregisterLink(link, object):
        """Unregisters a given link/object pair at the database.

           If the given link isn't referenced by any object anymore, it will 
           be removed from the database completely.

           Raises KeyError if the given pair isn't registered.

           Returns None.
        """

    def unregisterObject(object):
        """Unregisters all links for this object.

           Returns None.
        """

    def getLinksForObject(object):
        """Retrieve information about an object.

           Returns a list of ILink objects. 
           Returns an empty list if the object hasn't been registered yet.
        """

    def getLinksForURL(url):
        """Retrieve links for an url.

        Returns all links that point to the given url.
        """

    def getAllLinks():
        """Returns a list of all ILink objects.

           Warning: This is likely to be a slow method in large data sets.
        """

    def getAllLinkIds():
        """Returns a list of the ids of all ILink objects.

           Warning: This is likely to be a slow method in large data sets.
        """

    def getLinkCount():
        """Returns the amount of links currently in the database."""

    def queryLinks(self, **args):
        """Returns the result of querying the ZCatalog that indexes links."""

    def queryURLs(self, **args):
        """Returns the result of querying the ZCatalog that indexes urls."""


class IRetrieveManager(Interface):
    """Utility to perform link retrieval."""

    def retrieveObject(object):
        """Retrieves the links from the given object."""

    def retrieveSite():
        """Retrieves the links from all objects in the site.

           Raises RuntimeError if no connection to the lms can be established.
        """

    def supportsRetrieving(object):
        """Tells if the object is supported for retrieving links."""

    def getAllRetrieverNames():
        """Returns the name of all available retrievers."""


class IGlobalRetrieverRegistry(Interface):
    """Process global registry that holds information
       about all system wide available retrievers.
    """

    def register(method, name, defaults=[]):
        """Register a retriever method globally under the given title and as a
           default for the given portal_types.

           Defaults are overwritten subsequently by later calls.

           Raises ValueError if the method has been registered already.

           Returns None
        """

    def getByName(name):
        """Returns a retriever by it's name.

           Raises KeyError if a retriever with this name doesn't exists.
        """

    def getDefault(type):
        """Returns the default retriever for a type.

           Raises KeyError if there is no retriever for the given type.
        """

    def listNames():
        """Returns a list of all retriever names."""


class IURL(Interface):
    """URL status information

    The URL as transmitted to the LMS. It must be absolute and include protocol
    and netlocation.

    A URL can be referred to by many links as, depending on the context, a URL
    can be expressed by several relative spellings.

    """

    url = Attribute("Contains the URL the link refers to.")
    registered = Attribute("Has this link been registered with the web service?")
    lastcheck = Attribute("DateTime when the last check was performed.") 
    lastupdate = Attribute("DateTime when the last status change ocurred.")
    laststate = Attribute("The state before the current state was assumed.")
    state = Attribute("The current state of the link. Can be one of ['red', " \
                      "'green', 'orange', 'blue', 'grey'].")
    reason = Attribute("A verbose reason describing the error")
    links = Attribute(
        "A property that returns all currently associated links"
        "(as catalog brains).")

    def updateStatus(state, reason):
        """Updates the status information for this URL."""


class ILink(Interface):
    """A link as used from an object."""

    link = Attribute("Link as stored on the object")
    object = Attribute("The UID of the object containing the link.")
    url = Attribute(
        "URL as computed from the link and the object as context.")

    # Fields to support caching of data
    state = Attribute("The current state of the URL.")
    reason = Attribute("The current state of the URL.")

    def getObject():
        """Returns a list of objects referencing this link."""

    def getURL():
        """Return the URL object this link refers to."""


class IRetriever(Interface):
    """A class that implements a routine to retrieve and update URLs stored on
    an object.
    """

    def retrieveLinks():
        """Finds all links from the object and return them.

           Returns a list of URLs.

        """

    def updateLink(oldurl, newurl):
        """Replace all occurances of <oldurl> on object with <newurl>."""
