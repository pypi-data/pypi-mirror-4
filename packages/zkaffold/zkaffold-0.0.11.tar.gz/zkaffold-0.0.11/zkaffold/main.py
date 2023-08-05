# $Id: main.py 7851 2010-10-18 15:10:16Z karen $

"""
zkaffold.py
-----------

This creates a Plone site with an extension profile. It will build out from
the file content/structure.xml. Oh and your site id  will be 'portal', so there.
This will work for Plone 2.5 or Plone 3 sites

Run this with bin/zopectl run:
./bin/zopectl run ./lib/python/zkaffold/zkaffold.py product zopeuser

to include test content add the -u parameter (this assumes that you have a top
level directory called 'content' and that testcontent.xml is in it):
/bin/zopectl run ./lib/python/zkaffold/zkaffold.py -u testcontent.xml product zopeuser

To override the default 'content' directory add the -d parameter with the name of the
directory:
/bin/zopectl run ./lib/python/zkaffold/zkaffold.py -u testcontent.xml -d othercontent product zopeuser

Features
--------
 - delete content
 - install content
 - install products
 - apply zope interfaces
 - install test content
 - modify content
"""

__author__ = "Pat Smith <pat@isotoma.com>"
__version__ = "$Revision: 7851 $"[11:-2]
__docformat__ = "restructuredtext en"

import sys
import getopt
import transaction

from exceptions import ValueError

from Products.CMFPlone.utils import getFSVersionTuple
from Products.CMFPlone.utils import getToolByName

from zkaffold.consolehelpers  import login
from zkaffold.contentimporter import ContentImporter
from zkaffold.memberimporter  import MemberImporter
from zkaffold.build_site import build_site

DEFAULT_MANAGER = 'zopeadmin'
SITE_NAME = 'portal'

# Grab options and validate
try:
    opts, pargs = getopt.getopt(sys.argv[1:], 'u:d:', ['use-content=','use-directory='])
except getopt.error, msg:
    raise RuntimeError, msg

if len(pargs) == 0:
    print "\nUSAGE: zkaffold [-u <content.xml>] product [zopeuser]\n"
    raise ValueError, "You must supply a product to install"

productName = pargs[0]
if len(pargs) == 1:
    manager = DEFAULT_MANAGER
else:
    manager = pargs[1]

contentFile = None
content_dir = 'content'
for o, a in opts:
    if o in ("-u", "--use-content"):
        contentFile = a
    if o in ("-d", "--use-directory"):
        content_dir = a
        
app = build_site(app, manager, SITE_NAME, productName)

# Build out site structure
ci = ContentImporter('structure.xml', content_dir)
ci.importContent(app)
if contentFile != None:
    ci = ContentImporter(contentFile, content_dir)
    ci.importContent(app)
# Refresh catalog indexes for interfaces
pc = getToolByName(app.portal, 'portal_catalog')
pc.refreshCatalog()
# Import Members
mi = MemberImporter('members.xml', content_dir)
mi.importMembers(app.portal)

transaction.commit()
