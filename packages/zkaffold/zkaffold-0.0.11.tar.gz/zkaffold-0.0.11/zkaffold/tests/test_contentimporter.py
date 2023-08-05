# $Id$

__author__ = 'Karen Chan <karen.chan@isotoma.com>'
__docformat__ = 'restructuredtext en'
__version__ = '$Revision$'[11:-2]

import unittest

from zkaffold import contentimporter
from zkaffold.tests import functional


PUBLISH_XML = '''<?xml version="1.0" encoding="utf-8"?>
<transitions>
    <publish>
        <for>simple_publication_workflow</for>
        <for>folder_workflow</for>
        <steps>
            <step>something</step>
            <step>publish</step>
        </steps>
    </publish>
    <publish>
        <for>intranet_workflow</for>
        <steps>
            <step>publish_internally</step>
        </steps>
    </publish>
    <publish state="externally">
        <for>intranet_workflow</for>
        <steps>
            <step>publish_internally</step>
            <step>publish_externally</step>
        </steps>
    </publish>
</transitions>
'''


class TestContentImporter(unittest.TestCase):
    def test__parse_publish_xml(self):
        importer = contentimporter.ContentImporter(content_xml='<root></root>')
        self.assertEqual(importer._parse_publish_xml(PUBLISH_XML), {
            u'published': {
                u'simple_publication_workflow': [
                    u'something',
                    u'publish',
                    ],
                u'folder_workflow': [
                    u'something',
                    u'publish',
                    ],
                u'intranet_workflow': [
                    u'publish_internally',
                    ],
                },
            u'externally': {
                u'intranet_workflow': [
                    u'publish_internally',
                    u'publish_externally',
                    ],
                },
            })


class ContentImporterFunctionalTests(functional.FunctionalTestCase):
    def test_publish(self):
        importer = contentimporter.ContentImporter(content_xml='<root></root>',
                publish_xml=PUBLISH_XML)
        wf = self.portal.portal_workflow
        wf.setChainForPortalTypes(('Document',), ('intranet_workflow',))

        self.loginAsPortalOwner()
        self.portal.invokeFactory('Document', 'test-publish')
        importer.publish(self.portal['test-publish'])
        self.assertEqual(wf.getInfoFor(self.portal['test-publish'],
            'review_state'), 'internally_published')

        self.portal.invokeFactory('Document', 'test-external-publish')
        importer.publish(self.portal['test-external-publish'], state='externally')
        self.assertEqual(wf.getInfoFor(self.portal['test-external-publish'],
            'review_state'), 'external')


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestContentImporter))
    suite.addTest(unittest.makeSuite(ContentImporterFunctionalTests))
    return suite
