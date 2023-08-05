from Products.CMFCore.utils import getToolByName

tt = getToolByName(context, "portal_types")

types = tt.listTypeInfo()
types.sort(lambda a, b: cmp(a.getId(), b.getId()))

return types
