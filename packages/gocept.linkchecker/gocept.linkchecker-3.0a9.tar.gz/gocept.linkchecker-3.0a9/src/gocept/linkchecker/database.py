# Copyright (c) 2003-2006 gocept gmbh & co. kg
# See also LICENSE.txt
# 
"""CMF link checker tool - link database"""

from AccessControl import getSecurityManager, ClassSecurityInfo
from Globals import InitializeClass
from Products.BTreeFolder2.BTreeFolder2 import BTreeFolder2
from Products.CMFCore import permissions
from gocept.linkchecker import permissions
from gocept.linkchecker.interfaces import ILinkDatabase
from xmlrpclib import ServerProxy, Fault
from zExceptions import Unauthorized
import Products.Archetypes.interfaces
import Products.CMFCore.utils
import gocept.linkchecker.link
import gocept.linkchecker.log as log
import gocept.linkchecker.url
import gocept.linkchecker.utils
import socket
import zope.interface


PROTOCOL_VERSION = 2
WEBSERVICE = "http://lms.gocept.com/v2"

WEBSERVICE_STATEMAP = {
    "unknown" : "grey",
    "unsupported protocol": "blue",
    "ok" : "green",
    "temporary unavailable": "orange",
    "unavailable": "red"}


class OfflineWebserviceDummy(object):
    """An offline dummy for the web service."""

    def __init__(self):
        self.set_notifications = []
        self.register_many = []
        self.unregister_many = []

    def setClientNotifications(self, option):
        self.set_notifications.append(option)

    def registerManyLinks(self, links):
        self.register_many.append(links)
        return [(link, 'unknown', 'somereason') for link in links]

    def unregisterManyLinks(self, links):
        self.unregister_many.append(links)

offline_webservice = OfflineWebserviceDummy()


def manage_addLinkDatabase(container, id):
    """Add a new link database to a link manager."""
    container._setObject(id, LinkDatabase(id))


class LinkDatabase(BTreeFolder2):
    """A database of links. 

    Manages the physical storage of link and url information.
    """

    zope.interface.implements(ILinkDatabase)

    defaultURLPrefix = ""

    webservice = WEBSERVICE
    clientid = "change_me"
    password = ""

    offline = False

    security = ClassSecurityInfo()

    def getLinkCheckerDatabase(self):
        """Retrieve this object with a meaningful name via acquisition."""
        return self.aq_inner

    def manage_afterAdd(self, item, container):
        LinkDatabase.inheritedAttribute('manage_afterAdd')(self, item,
                                                           container)

        def insertIndexes(catalog, indexes):
            existing = catalog.Indexes.objectIds()
            for index_name, index_type in indexes:
                if index_name not in existing:
                    catalog.addIndex(index_name, index_type)

        def insertCacheColumns(catalog, columns):
            existing_columns = catalog.schema()
            for c, value in columns:
                if c not in existing_columns:
                    catalog.addColumn(c, value)

        # Setup the link catalog
        if 'link_catalog' not in self.objectIds():
            self.manage_addProduct['ZCatalog'].\
                    manage_addZCatalog('link_catalog', 'Link catalog')
        indexes = [('state', 'KeywordIndex'),
                   ('url', 'FieldIndex'),
                   ('object', 'KeywordIndex')]
        insertIndexes(self.link_catalog, indexes)

        columns = [("object", None),
                   ("url", ""),
                   ("reason", ""),
                   ("lastcheck", ""),
                   ("state", ""),
                   ("link", ""),
                   ("getId", "")]
        insertCacheColumns(self.link_catalog, columns)

        # Setup the url catalog
        if 'url_catalog' not in self.objectIds():
            self.manage_addProduct['ZCatalog'].\
                    manage_addZCatalog('url_catalog', 'URL catalog')
        indexes = [('url', 'FieldIndex'),
                   ('registered', 'FieldIndex')]
        insertIndexes(self.url_catalog, indexes)

        columns = [("url", ""),
                   ("id", ""),
                   ("reason", ""),
                   ("lastcheck", ""),
                   ("state", "grey")]
        insertCacheColumns(self.url_catalog, columns)

    ###############
    # ILinkDatabase

    security.declareProtected(permissions.ManagePortal, 'configure')
    def configure(self, defaultURLPrefix=None, clientid=None, password=None,
                  webservice=None, client_notifications=None):
        """Set configuration values."""
        if clientid is not None:
            self.clientid = clientid
        if password:
            self.password = password
        if defaultURLPrefix is not None:
            self.defaultURLPrefix = defaultURLPrefix
        if webservice is not None:
            self.webservice = webservice

        # need to reconfigure connection
        try:
            delattr(self, '_v_lms_client')
        except AttributeError:
            pass

        if client_notifications is not None:
            server = self._getWebServiceConnection()
            if server is not None:
                server.setClientNotifications(client_notifications)

    security.declareProtected(
        permissions.USE_LINK_MANAGEMENT, 'registerLinks')
    def registerLinks(self, links, object, online=True):
        """Registers links for an object at the database."""
        sm = getSecurityManager()
        if not sm.checkPermission(
            permissions.ModifyPortalContent, object):
            raise Unauthorized, \
                "Can't modify link registrations for this object."
        link_objects = [self._register_link(link, object) for link in links]
        if online:
            urls = [link.getURL()
                    for link in link_objects
                    if link is not None]
            self._register_urls_at_lms(urls)

    def _register_link(self, link, object):
        link_id = gocept.linkchecker.utils.hash_link(link, object)
        if link_id in self.objectIds():
            return
        link = gocept.linkchecker.link.Link(link, link_id, object.UID())
        # Now we can add the link to the database
        self._setObject(link_id, link)
        return self[link_id]

    security.declarePrivate("_updateWSRegistrations")
    def _updateWSRegistrations(self):
        """Registers a link with the webservice. 

        May also register yet non-registered other links.
        """
        unregistered = self.queryURLs(registered=False)
        unregistered = [x.getObject() for x in unregistered]
        # Nothing to do?
        if not unregistered:
            return
        self._register_urls_at_lms(unregistered)

    def _register_urls_at_lms(self, url_objects):
        """Register the given URL objects at the LMS web service.
        """
        # Do we have an LMS connection?
        lms = self._getWebServiceConnection()
        if lms is None:
            return
        urls = [url.url for url in url_objects]
        states = lms.registerManyLinks(urls)
        # The server *may* report the status of URls it already knows.
        for url, state, reason in states:
            state = WEBSERVICE_STATEMAP[state]
            url = self[gocept.linkchecker.utils.hash_url(url)]
            url.updateStatus(state, reason)
        # Mark all of the URLs as registered
        for url in url_objects:
            url.registered = True

    security.declarePrivate('unregisterLink')
    def unregisterLink(self, link, object):
        """Unregisters a given link/object pair at the database.

           If the given link isn't referenced by any object anymore, it will 
           be removed from the database completely.

           Returns None.
        """
        id = gocept.linkchecker.utils.hash_link(link)
        self.manage_delObject(id)

    security.declarePrivate('unregisterObject')
    def unregisterObject(self, object):
        """Unregisters all links for this object.

           Returns None.
        """
        if isinstance(object, (gocept.linkchecker.url.URL,
                               gocept.linkchecker.link.Link)):
            return
        links = self.getLinksForObject(object)
        link_ids = [x.getId() for x in links]
        self.manage_delObjects(link_ids)

    def _getWebServiceConnection(self):
        """return connection to lms

        returns LMSClient instance if connection is ok
        returns None if connection is not Ok
        """
        conn = self.checkConnection()
        if conn.ok:
            client = self._get_connection_object()
        else:
            log.logger.error('Connection to LMS not possible: %s' % (conn.error, ))
            if self.offline:
                client = offline_webservice
            else:
                client = None
        return client

    def _get_connection_object(self):
        client = getattr(self, '_v_lms_client', None)
        if client is None:
            client = LMSClient(self.webservice, self.clientid, self.password)
            self._v_lms_client = client
        return client

    def _deleteURLs(self, urls):
        # Unregister with LMS
        lms = self._getWebServiceConnection()
        if lms is None:
            return
        self.manage_delObjects([url.id for url in urls])
        lms.unregisterManyLinks([url.url for url in urls])

    security.declareProtected(permissions.USE_LINK_MANAGEMENT, 'getLinksForURL')
    def getLinksForURL(self, url):
        """Retrieve links for an url."""
        links = [x.getObject() for x in self.queryLinks(url=url)]
        links = filter(None, links)
        return links

    security.declareProtected(permissions.USE_LINK_MANAGEMENT, 'getLinksForObject')
    def getLinksForObject(self, object, state=None):
        """Retrieve information about an object.

           Returns a list of ILink objects.
           Returns an empty list if the object hasn't been registered yet.
        """
        sm = getSecurityManager()
        if not sm.checkPermission(
            permissions.AccessContentsInformation, object):
            raise Unauthorized, "Can't view links on this object."
        if not Products.Archetypes.interfaces.IReferenceable.providedBy(object):
            return []

        uid = object.UID()
        if uid is None:
            links = []
        else:
            query_args = {}
            if state is not None:
                query_args['state' ] = state
            links = self.queryLinks(object=[uid], **query_args)
            links = [x.getObject() for x in links]
            links = filter(None, links)
        return links

    security.declareProtected(permissions.USE_LINK_MANAGEMENT, 'getAllLinks')
    def getAllLinks(self):
        """Returns a list of all ILink objects.

           Warning: This is likely to be a slow method in large data sets.
        """
        return self.objectValues(['Link'])

    security.declareProtected(permissions.USE_LINK_MANAGEMENT, 'getAllLinkIds')
    def getAllLinkIds(self):
        """Returns a list of the ids of all ILink objects.

           Warning: This is likely to be a slow method in large data sets.
        """
        return self.objectIds(['Link'])

    security.declareProtected(
        permissions.USE_LINK_MANAGEMENT, 'getLinkIterator')
    def getLinkIterator(self):
        """returns generator for all link objects"""
        for id in self.getAllLinkIds():
            yield self.get(id)

    security.declareProtected(permissions.USE_LINK_MANAGEMENT, 'getLinkCount')
    def getLinkCount(self):
        """Returns the amount of links currently in the database."""
        return len(self.queryLinks())

    security.declareProtected(permissions.USE_LINK_MANAGEMENT, 'queryLinks')
    def queryLinks(self, **args):
        """Returns the result of querying the ZCatalog that indexes links."""
        return self.link_catalog(**args)

    security.declareProtected(permissions.USE_LINK_MANAGEMENT, 'queryURLs')
    def queryURLs(self, **args):
        """Returns the result of querying the ZCatalog that indexes urls."""
        return self.url_catalog(**args)

    security.declareProtected(
        permissions.ManagePortal, 'sync')
    def sync(self):
        lms = self._getWebServiceConnection()
        lms.forceSynchronization()

    security.declareProtected(
        permissions.ManagePortal, 'updateLinkStatus')
    def updateLinkStatus(self, url, state, reason):
        """XML-RPC connector for LMS"""
        state = WEBSERVICE_STATEMAP[state]
        for url in self.queryURLs(url=url):
            url = url.getObject()
            url.updateStatus(state, reason)

    security.declarePublic('updateManyStates')
    def updateManyStates(self, client_id, password, update_list):
        """XML-RPC connector for LMS"""
        self.authenticateXMLRPC(client_id, password)
        for url, state, reason in update_list:
            self.updateLinkStatus(url, state, reason)

    security.declarePublic('xmlrpc_getAllLinks')
    def xmlrpc_getAllLinks(self, client_id, password):
        """XML-RPC connector for LMS

           returns all links for LMS
        """
        self.authenticateXMLRPC(client_id, password)
        # XXX optimiziation: make .url unique
        return [x.url for x in self.queryURLs()]

    security.declarePrivate('authenticateXMLRPC')
    def authenticateXMLRPC(self, client_id, password):
        """authenticates XML remote call"""
        if not (client_id == self.clientid and\
                password == self.password):
            raise Unauthorized,\
                "Client-Id or password do not match."

    security.declareProtected(
        permissions.ManagePortal, 'updateAllStatus')
    def updateAllStatus(self):
        """Manually update all link status'
        """
        server = self._getWebServiceConnection()
        if server is None:
            return
        for url in self.queryURLs():
            try:
                status, reason = server.getStatus(url.url)
            except KeyError:
                # not registered with server
                server.registerLink(url.url)
                status = 'temporary unavailable'
                reason = 'No status response from LMS yet.'
            status = WEBSERVICE_STATEMAP[status]
            if url.state != status:
                url = url.getObject()
                url.updateStatus(status, reason)

    security.declareProtected(
        permissions.USE_LINK_MANAGEMENT, 'checkConnection')
    def checkConnection(self):
        """return if connection is up and running

            returns r.ok == True if connection is ok
            returns r.ok == False if connection is *not* ok
                sets also r.error to some error information
        """
        class R:
            __allow_access_to_unprotected_subobjects__ = 1
            def __init__(self, **kwargs):
                self.__dict__.update(kwargs)

        try:
            server = self._get_connection_object()
        except Exception, e:
            ok = False
            error = '%s: %s' % (str(e.__class__), str(e))
            protocol_version='unknown',
        else:
            ok, protocol_version, error = server.checkConnection()
        r = R(ok=ok, error=error,
              client_protocol=PROTOCOL_VERSION,
              server_protocol=protocol_version)
        return r

    security.declareProtected(
        permissions.ManagePortal, 'getClientNotifications')
    def getClientNotifications(self):
        server = self._getWebServiceConnection()
        if server is None:
            return False
        stat = server.getClientNotifications()
        return stat

    security.declareProtected(permissions.ManagePortal, 
                              'getInfoFrameURL')
    def getInfoFrameURL(self):
        """Returns the URL received from the LMS or an empty string."""
        server = self._getWebServiceConnection()
        if server is None:
            return ""
        return server.getInfoFrameURL()


class LMSClient:
    """client to lms"""

    _exception_mapping = {
        'KeyError': KeyError,
    }

    def __init__(self, url, client_id, password):
        self.url = url
        self.client_id = client_id
        self.password = password
        self._server = ServerProxy(url)

    def forceSynchronization(self):
        self._server.forceSynchronization(self.client_id, self.password)

    def registerManyLinks(self, urls):
        result = []
        if urls:
            try:
                result = self._server.registerURLs(self.client_id, self.password, urls)
            except Fault, f:
                self._translate_fault(f)
        return result

    def unregisterManyLinks(self, urls):
        if not urls:
            return []
        try:
            result = self._server.unregisterURLs(self.client_id, self.password, urls)
        except Fault, f:
            self._translate_fault(f)
        return result

    def getStatus(self, url):
        try:
            status = self._server.getStatus(url)
        except Fault, f:
            self._translate_fault(f)
        return status

    def getClientNotifications(self):
        try:
            return self._server.getClientNotifications(self.client_id, self.password)
        except Fault, f:
            self._translate_fault(f)

    def getInfoFrameURL(self):
        try:
            return self._server.getInfoFrameURL(self.client_id, self.password)
        except Fault, f:
            self._translate_fault(f)

    def setClientNotifications(self, status):
        if isinstance(status, (str, unicode)):
            status = int(status)
        if isinstance(status, int):
            status = bool(status)
        self._server.setClientNotifications(self.client_id, self.password, status)

    def checkConnection(self):
        is_ok = False
        error = 'unknown'

        protocol_version = None
        try:
            protocol_version = self._server.checkConnection(self.client_id, self.password)
        except Fault, f:
            error = '%s (%s)' % (f.faultString, f.faultCode)
        except socket.error, e:
            e_code, e_string = e.args
            error = 'socket.error: %s (%s)' % (e_string, e_code)
        except Exception, e:
            error = str(e)
        else:
            if protocol_version == PROTOCOL_VERSION:
               is_ok = True 
            else:
               error = ("Incompatible protocol version. " 
                        "Got: %s, expected: %s" % (protocol_version,
                                                   PROTOCOL_VERSION))
        return is_ok, protocol_version, error

    #########
    # private

    def _translate_fault(self, f):
        name, value = f.faultCode, f.faultString

        exception_class = self._exception_mapping.get(name)
        if exception_class is None:
            sm = zope.component.getSiteManager()
            Products.CMFCore.utils.getToolByName(
                sm, "plone_utils").addPortalMessage(
                    "LMS Error: %s/%s" % (name, value), type='error')
        else:
            e = exception_class(value)
            raise e


InitializeClass(LinkDatabase)
