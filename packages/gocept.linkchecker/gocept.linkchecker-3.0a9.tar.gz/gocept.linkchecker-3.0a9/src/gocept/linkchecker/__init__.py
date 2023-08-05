# Copyright (c) 2005 gocept. All rights reserved.
# See also LICENSE.txt
# 
"""CMF link checker tool initalisation code"""

from gocept.linkchecker import permissions
from Products.CMFCore import utils as CMFutils
from Products.CMFCore import DirectoryView


def initialize_tool(context):
    from gocept.linkchecker import LinkCheckerTool
    tools = (LinkCheckerTool.LinkCheckerTool, )
    tool_init = CMFutils.ToolInit('Link checker tool',
                                  tools=tools,
                                  icon="tool.png")
    tool_init.initialize(context)
   
def initialize_content(context):
    from gocept.linkchecker import database, retrievemanager, reports
    context.registerClass(database.LinkDatabase,
                          constructors=(database.manage_addLinkDatabase,),
                          container_filter = filterLinkManagerAddable)
    context.registerClass(reports.BaseReports,
                          constructors=(reports.manage_addBaseReports,),
                          container_filter=filterLinkManagerAddable)

    context.registerClass(retrievemanager.RetrieveManager,
                          constructors=(retrievemanager.\
                                        manage_addRetrieveManager,),
                          container_filter=filterLinkManagerAddable
        )


def initialize(context):
    initialize_tool(context)
    initialize_content(context)
    DirectoryView.registerDirectory('skins', globals())
    

def filterLinkManagerAddable(objectmanager):
    """Tools for the Link Manager should not be addable everywhere"""
    if objectmanager.meta_type != "CMF Linkchecker Tool":
        return False
    return True
