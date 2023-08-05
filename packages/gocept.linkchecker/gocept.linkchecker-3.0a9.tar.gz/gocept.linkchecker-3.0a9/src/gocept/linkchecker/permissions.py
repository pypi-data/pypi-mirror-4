##############################################################################
#
# Copyright (c) 2003 gocept gmbh & co. kg. All rights reserved.
#
# See also LICENSE.txt
#
##############################################################################
"""CMF link checker tool interface definitions"""



from Products.CMFCore.permissions import *

RUN_MAIL_NOTIFICATIONS = "Linkchecker: Run mail notifications"
USE_LINK_MANAGEMENT = "Linkchecker: Use link management functions"

# XXX initialize the permissions with default roles
#    MAIL -> manager
# USE_LINK_MANAGEMENT -> member
