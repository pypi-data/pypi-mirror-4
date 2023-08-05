# $Id: build_site.py 4550 2010-01-24 10:54:19Z karen $

'''
build_site.py
-------------
'''

__author__ = 'Karen Chan <karen@isotoma.com>'
__docformat__ = 'restructuredtext en'
__version__ = '$Revision: 4550 $'[11:-2]

from Products.CMFPlone.utils import getFSVersionTuple
from Products.CMFPlone.utils import getToolByName

from consolehelpers import login

def build_site(app, manager, site_name, productName=None):
    #login as manager
    app = login(app, manager)

    # Delete and re-create the portal
    if hasattr(app, site_name):
        print 'Deleting old portal'
        app.manage_delObjects(site_name)

    # Install the product
    version = getFSVersionTuple()
    factory = app.manage_addProduct['CMFPlone']
    if version[0] <= 2:
        ext_id = '%s:default' % productName
        factory.addPloneSite(site_name, productName, extension_ids=(ext_id,))
    else:
        # Plone 3 and above
        factory.addPloneSite(site_name)
        if productName:
            qi = getToolByName(getattr(app, site_name), 'portal_quickinstaller')
            qi.installProducts([productName,])

    return app
