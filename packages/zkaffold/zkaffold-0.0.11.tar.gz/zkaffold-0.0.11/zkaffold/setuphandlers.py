# $Id: setuphandlers.py 7861 2010-10-18 15:12:04Z karen $

'''
setuphandlers.py
'''

__author__ = 'Karen Chan <karen@isotoma.com>'
__docformat__ = 'restructuredtext en'
__version__ = '$Revision: 7861 $'[11:-2]


from zope.component.interfaces import ComponentLookupError
from zope.interface import implements

from Products.CMFPlone.interfaces import (
        INonInstallable as INonInstallableProfiles)
from Products.CMFQuickInstallerTool.interfaces import (
        INonInstallable as INonInstallableProducts)

import contentexporter


class HiddenProfiles(object):
    implements(INonInstallableProfiles)

    def getNonInstallableProfiles(self):
        return [u'zkaffold']


class HiddenProducts(object):
    implements(INonInstallableProducts)

    def getNonInstallableProducts(self):
        return [u'zkaffold']


def zkaffold_various(context):
    """Setup zkaffold.
    """
    if not context.readDataFile('zkaffold.txt'):
        return

    portal = context.getSite()

    # Create a single IContentExporter utility for the portal
    sm = portal.getSiteManager()
    try:
        sm.getUtility(contentexporter.IContentExporter)
    except ComponentLookupError:
        sm.registerUtility(contentexporter.ContentExporter(),
                contentexporter.IContentExporter)
