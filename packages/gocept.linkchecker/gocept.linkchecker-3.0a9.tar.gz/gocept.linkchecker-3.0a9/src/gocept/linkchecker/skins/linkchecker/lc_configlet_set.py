##parameters=defaultURLPrefix, clientid, password, webservice, client_notifications=None

# Copyright (c) 2003-2005 gocept gmbh & co. kg
# See also LICENSE.txt
# 

from Products.CMFCore.utils import getToolByName

lc = getToolByName(context, 'portal_linkchecker')
lc.database.configure(defaultURLPrefix=defaultURLPrefix,
                      clientid=clientid,
                      password=password,
                      webservice=webservice,
                      client_notifications=client_notifications)

context.REQUEST.RESPONSE.redirect(
                        'lc_configlet?portal_status_message=Changes+saved.')
