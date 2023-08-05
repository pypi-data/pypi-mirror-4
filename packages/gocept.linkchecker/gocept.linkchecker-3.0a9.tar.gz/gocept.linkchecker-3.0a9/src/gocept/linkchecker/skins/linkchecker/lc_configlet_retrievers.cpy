from Products.CMFCore.utils import getToolByName

tt = getToolByName(context, "portal_types")
lc = getToolByName(context, "portal_linkchecker")
form = context.REQUEST.form
formkeys = form.keys()

types = tt.listTypeInfo()
registerRetriever = lc.retrieving.registerRetriever

for typeinfo in types:
    portal_type = typeinfo.getId()
    retriever = form.get(portal_type)
    if retriever is None:
        # not in form
        continue
    if retriever == '':
        # remove mapping
        retriever = None
    registerRetriever(portal_type, retriever)

state.set(portal_status_message='Your changes have been saved.')

return state
