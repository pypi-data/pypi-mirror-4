##############################################################################
#
# Copyright (c) 2003 gocept gmbh & co. kg. All rights reserved.
#
# See also LICENSE.txt
#
##############################################################################
"""A short script that shortens URLs in a readable fashion to a target length.
"""


import urlparse
                
def shortURL(url, target=50, base=""):

    if len(url) <= target:
        return url 

    if url.startswith(base):
        url = url[len(base):]

    scheme, location, path, parameters, query, fragment = \
        urlparse.urlparse(url)

    for check, filter in filters:
        url_ = urlparse.urlunparse((scheme, location, path, parameters, query, fragment))
        if len(url_) < target:
            break
        if check(scheme, location, path, parameters, query, fragment):
            scheme, location, path, parameters, query, fragment = \
                filter(scheme, location, path, parameters, query, fragment)
            break

    url_ = urlparse.urlunparse((scheme, location, path, parameters, query, fragment))

    if url_ == url:
        return url_

    if url_ <= target:
        return url_

    return shortURL(url_, target)

checkPath = lambda s,l,p,pa,q,f: 1
def plugPath(schema, location, path, parameters, query, fragment):
    path = path.split('/')
    path = [ x for x in path if x != "..." ]
    path = path[:len(path)//2] + ["..."] + path[len(path)//2+1:]
    path = "/".join(path)
    return schema, location, path, parameters, query, fragment

checkParameters = lambda s,l,p,pa,q,f: len(pa) > 3
def plugParameters(schema, location, path, parameters, query, fragment):
    parameters = "..."
    return schema, location, path, parameters, query, fragment
    
checkQuery = lambda s,l,p,pa,q,f: len(q) > 3
def plugQuery(schema, location, path, parameters, query, fragment):
    query = "..."
    return schema, location, path, parameters, query, fragment
    
checkFragment = lambda s,l,p,pa,q,f: len(f) > 3
def plugFragment(schema, location, path, parameters, query, fragment):
    fragment = "..."
    return schema, location, path, parameters, query, fragment


filters = [ (checkFragment, plugFragment), 
            (checkQuery, plugQuery), 
            (checkParameters, plugParameters), 
            (checkPath, plugPath), ]
