from Products.CMFCore.utils import getToolByName

lc = getToolByName(context, 'portal_linkchecker')
links = lc.database.getLinksForObject(context, state=['red', 'orange'])
return links
