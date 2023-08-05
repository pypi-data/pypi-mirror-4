import sys
import DateTime # zope
import transaction
import datetime
import ZODB.POSException
from AccessControl.SecurityManagement import \
    newSecurityManager, setSecurityManager
from Testing.makerequest import makerequest
import cPickle

site = app.unrestrictedTraverse(sys.argv[1])

print "Logging in as %s" % sys.argv[2]
user = site.acl_users.getUser(sys.argv[2])

newSecurityManager(None, user)
site = makerequest(app).unrestrictedTraverse(sys.argv[1])

last = DateTime.DateTime('1970/01/01')

start = datetime.datetime.now()
indexed = 0
retrieving = site.portal_linkchecker.retrieving

try:
    seen = cPickle.load(open('crawl.status', 'r'))
    print "Loaded status"
except:
    print "Starting fresh"
    seen = set()


print "Fetching brains from catalog ..."
docs_remaining = site.portal_catalog.searchResults(Language='all')
docs_iter = iter(docs_remaining)

final = False
while not final:
    print "Scanning for items not retrieved in current run ..."

    skipped = 0
    seen_this = set()
    batch_start = datetime.datetime.now()

    for doc in docs_iter:
        if (datetime.datetime.now() - batch_start) > datetime.timedelta(seconds=30):
            # Time out a batch after 15 seconds
            break
        if doc.getRID() in seen:
            skipped += 1
            continue
        seen_this.add(doc.getRID())
        try:
            d = doc.getObject()
	    a = datetime.datetime.now()
            retrieving.retrieveObject(d, online=False)
	    print "retrieved %s in %s" % (doc.getPath(), datetime.datetime.now() - a)
        except Exception, e:
            print "Crawl raised an error for %s: %s" % (doc.getPath(), str(e))
            continue
    else:
        final = True
    indexed += len(seen_this)
    time_passed = datetime.datetime.now() - start
    time_per_doc = (time_passed.days * (24*3600) + time_passed.seconds) / float(indexed)
    time_remaining = (len(docs_remaining) - len(seen) - len(seen_this)) * time_per_doc
    print "Retrieved %s (%s total, %s indexed, %s skipped) documents in %s (%.04ss/doc, %s remaining)" % (
        len(seen_this), len(docs_remaining), indexed, skipped, time_passed, time_per_doc, datetime.timedelta(seconds=int(time_remaining)))
    try:
        transaction.commit()
    except ZODB.POSException.ConflictError:
        print "Conflict. Continuing with next batch."
        transaction.abort()
        continue
    else:
    	a = datetime.datetime.now()
        seen.update(seen_this)
        cPickle.dump(seen, open('crawl.status', 'w'))
	print "saved in %s" % (datetime.datetime.now() - a)

print "Forcing synchronisation with LMS"
site.portal_linkchecker.database.sync()

transaction.commit()
