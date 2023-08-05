from Products.CMFCore.utils import getToolByName

lc = getToolByName(context, 'portal_linkchecker')
rc = getToolByName(context, 'reference_catalog')
portal_url = getToolByName(context, 'portal_url')()

if not lc.isUserAllowed():
    return []

object_uids = []

urls = [
 lc.resolveRelativeLink(context.getId(), context),
]

if hasattr(context, "UID"):
    try:
        uid = context.UID()
    except:
        # this might break in various ways *IF* context is not an archetype.
        # we just ignore it then
        pass
    if uid:
        # Some objects may not get a UID, we ignore those too.
        urls.append(portal_url+"/resolveuid/"+uid)

for url in urls:
    brains = lc.database.queryLinks(url=url)
    for b in brains:
        object_uids.append(b.object)

objects = []
for uid in object_uids:
    obj = rc.lookupObject(uid)
    objects.append(obj)

return objects
