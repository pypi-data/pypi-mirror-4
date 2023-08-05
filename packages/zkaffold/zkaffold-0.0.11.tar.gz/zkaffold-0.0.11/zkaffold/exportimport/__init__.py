# $Id$

'''
Export and import handlers for zkaffold.xml
'''

__author__ = 'Karen Chan <karen@isotoma.com>'
__docformat__ = 'restructuredtext en'
__version__ = '$Revision$'[11:-2]

import os

from zope.component import getUtility, provideUtility
from zope.component.interfaces import ComponentLookupError

from zkaffold import contentexporter, contentimporter, memberimporter

_DIRECTORY = 'zkaffold'
_STRUCTURE_FILENAME = 'structure.xml'
_MEMBER_FILENAME = 'members.xml'
_PUBLISH_FILENAME = 'publish.xml'

def import_site_structure(context):
    """Import the site structure from _STRUCTURE_FILENAME and members from
    _MEMBER_FILENAME
    """
    portal = context.getSite()
    logger = context.getLogger('zkaffold')

    structure = context.readDataFile(os.path.join(_DIRECTORY,
        _STRUCTURE_FILENAME))
    if structure:
        def load_file(file_dir, filename):
            return context.readDataFile(os.path.join(file_dir, filename))

        publish = context.readDataFile(os.path.join(_DIRECTORY,
            _PUBLISH_FILENAME))

        importer = contentimporter.ContentImporter(
                importSource=_STRUCTURE_FILENAME,
                content_dir=_DIRECTORY,
                content_xml=structure,
                publish_xml=publish,
                load_file=load_file)
        importer.importContent(portal)
        logger.info('Site structure imported.')

    members = context.readDataFile(os.path.join(_DIRECTORY,
        _MEMBER_FILENAME))
    if members:
        importer = memberimporter.MemberImporter(members_xml=members)
        importer.importMembers(portal)

def export_site_structure(context):
    """Export a plone site to zkaffold xml.
    """
    portal = context.getSite()
    logger = context.getLogger('zkaffold')

    exporter = portal.getSiteManager().getUtility(
            contentexporter.IContentExporter)
    structure_xml, files = exporter.export_site_structure(portal, logger=logger)
    context.writeDataFile(_STRUCTURE_FILENAME,
            structure_xml, 'text/xml',
            subdir=_DIRECTORY)

    for filename, file_content in files.items():
        context.writeDataFile(filename, file_content,
                'application/octet-stream', subdir=_DIRECTORY)
