##parameters=object, old_link, new_link, return_to
from Products.CMFCore.utils import getToolByName

references = getToolByName(context, "reference_catalog")
lc = getToolByName(context, "portal_linkchecker")
object = references.lookupObject(object)
lc.retrieving.updateLink(old_link, new_link, object)

context.REQUEST.RESPONSE.redirect(return_to)
