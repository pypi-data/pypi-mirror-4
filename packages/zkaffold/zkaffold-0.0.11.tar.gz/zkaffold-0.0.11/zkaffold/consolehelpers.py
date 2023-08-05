# $Id: consolehelpers.py 4307 2009-12-14 15:29:20Z richardm $

"""
lib/python/consolehelpers.py
--------------------

Miscellaneous functions helpful for debugging / console ops
"""

__author__ = "Pat Smith <pat@isotoma.com>"
__version__ = "$Revision: 4307 $"[11:-2]
__docformat__ = "restructuredtext en"

from Acquisition import aq_base
from webdav.Lockable import wl_isLocked
from AccessControl.SecurityManagement import newSecurityManager
from Testing.makerequest import makerequest

def login(app, manager_user):
    user = app.acl_users.getUserById(manager_user).__of__(app.acl_users)
    newSecurityManager(None, user)
    return makerequest(app)

def dumpbrains(brains):
    for b in brains:
        print "%s\t\t:%s" % (b.id, b.getPath())

def gut(ob):
    for p in dir(ob):
        print p
        
""" Ensure all WebDAV locks below the given path are removed. Called before update. """
def unlockAllObjects(app, path):
    lockedobjs = findLockedObjects(app, path)
    for (o, p, i) in lockedobjs:
        errs = False
        for l in [li['token'] for li in i]:
            try:
                o.wl_delLock(l)
            except:
                errs = True
        if errs:
            # Only run clearLocks if we can't delete all locks normally
            o.wl_clearLocks()
    
################################################################################
# Stolen from App.DavLockManager:
#################################

def findLockedObjects(app, frompath=''):

    if frompath:
        if frompath[0] == '/': frompath = frompath[1:]
        # since the above will turn '/' into an empty string, check
        # for truth before chopping a final slash
        if frompath and frompath[-1] == '/': frompath= frompath[:-1]

    # Now we traverse to the node specified in the 'frompath' if
    # the user chose to filter the search, and run a ZopeFind with
    # the expression 'wl_isLocked()' to find locked objects.
    obj = app.unrestrictedTraverse(frompath)
    lockedobjs = __findapply(obj, path=frompath)

    return lockedobjs

# Changed original function to return object, rather than the path
def __findapply(obj, result=None, path=''):   
    # recursive function to actually dig through and find the locked
    # objects.

    if result is None:
        result = []
    base = aq_base(obj)
    if not hasattr(base, 'objectItems'):
        return result
    try: items = obj.objectItems()
    except: return result

    addresult = result.append
    for id, ob in items:
        if path: p = '%s/%s' % (path, id)
        else: p = id

        dflag = hasattr(ob, '_p_changed') and (ob._p_changed == None)
        bs = aq_base(ob)
        if wl_isLocked(ob):
            li = []
            addlockinfo = li.append
            for token, lock in ob.wl_lockItems():
                addlockinfo({'owner':lock.getCreatorPath(),
                             'token':token})
            addresult((ob, p, li))
            dflag = 0
        if hasattr(bs, 'objectItems'):
            __findapply(ob, result, p)
        if dflag: ob._p_deactivate()

    return result

################################################################################