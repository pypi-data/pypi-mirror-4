##parameters=redirect=1
lc = context.portal_linkchecker
lc.retrieving.retrieveObject(context)

if redirect:
    context.REQUEST.RESPONSE.redirect(context.absolute_url() + 
                                      '/lc_object_status')
