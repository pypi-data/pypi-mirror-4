request = context.REQUEST

if 'crawl' in request.form:
    context.portal_linkchecker.retrieving.retrieveSite()
    request.RESPONSE.redirect('lc_configlet?portal_status_message=The site was crawled.')
elif 'sync' in request.form:
    context.portal_linkchecker.database.sync()
    request.RESPONSE.redirect(
        'lc_configlet?portal_status_message=A syncronization with the LMS was requested.')
