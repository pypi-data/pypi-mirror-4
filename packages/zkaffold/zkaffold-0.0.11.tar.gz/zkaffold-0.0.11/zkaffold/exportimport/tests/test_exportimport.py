# -*- coding: utf-8 -*-
# $Id: test_exportimport.py 9567 2011-02-22 11:40:51Z karen $

'''
Tests for exportimport/__init__.py
'''

__author__ = 'Karen Chan <karen@isotoma.com>'
__docformat__ = 'restructuredtext en'
__version__ = '$Revision: 9567 $'[11:-2]

import os
import unittest

import mock

from zope.interface import Interface

from zkaffold.tests import functional
from zkaffold.exportimport import import_site_structure


class ITestZkaffoldInterface(Interface):
    """An interface for testing zkaffold
    """


class TestImportSiteStructure(functional.FunctionalTestCase):
    """Tests for import_site_structure
    """

    def afterSetUp(self):
        self.context = mock.Mock()
        self.context.getSite.return_value = self.portal

    def test_site_structure(self):
        structure_xml = '''<?xml version="1.0" encoding="utf-8"?>
<site xmlns:zkaffold="http://www.isotoma.com/zkaffold"
    image_dir="images_dir" file_dir="files_dir">

    <Document id="test-doc">
        <params>
            <param name="title" type="text">TEST</param>
            <param name="text" type="text"><![CDATA[<p>テスト</p>]]></param>
            <param name="excludeFromNav" type="boolean">True</param>
            <param name="relatedItems" type="reference_list">
                <items>
                    <item type="text">/folder/collection</item>
                    <item type="text">/event</item>
                </items>
            </param>
        </params>
    </Document>

    <Folder id="folder">
        <params>
            <param name="title" type="text">folder</param>
        </params>

        <Document id="default-page" is_default_page="True">
            <params>
                <param name="title" type="text">Folder landing page</param>
            </params>
        </Document>

        <Topic id="collection">
            <params>
                <param name="title" type="text">Collection</param>
                <param name="customView" type="boolean">True</param>
                <param name="customViewFields" type="list">
                    <items>
                        <item type="text">title</item>
                        <item type="text">CreationDate</item>
                        <item type="text">review_state</item>
                    </items>
                </param>
            </params>
        </Topic>

        <Link id="link">
            <params>
                <param name="title" type="text">Isotoma</param>
                <param name="remoteUrl" type="text">http://www.isotoma.com/</param>
            </params>
        </Link>

        <Folder id="downloads">
            <params>
                <param name="title" type="text">Downloads</param>
            </params>

            <File id="some-stuff.txt">
                <params>
                    <param name="title" type="text">Some stuff</param>
                    <param name="file" type="file">some-stuff.txt</param>
                </params>
            </File>

            <Image id="isotoma_logo.gif">
                <params>
                    <param name="title" type="text">Isotoma Logo</param>
                    <param name="image" type="image">isotoma_logo.gif</param>
                </params>
            </Image>
        </Folder>
    </Folder>

    <Event id="event">
        <params>
            <param name="title" type="text">イベント</param>
            <param name="startDate" type="date">2010-01-01</param>
            <param name="endDate" type="date">2011-01-01</param>
            <param name="contactName" type="text">karen</param>
            <param name="contactPhone" type="text">1234</param>
            <param name="subject" type="list">
                <items>
                    <item type="text">plone</item>
                </items>
            </param>
        </params>
    </Event>

    <old-event>
        <modify>
            <params>
                <param name="title" type="text">modified title</param>
            </params>
        </modify>
    </old-event>

    <zkaffold:object portal_type="News Item" id="news-item">
        <params>
            <param name="title" type="text">News item</param>
            <param name="image" type="image">isotoma_logo.gif</param>
            <param name="imageCaption" type="text">Image caption</param>
        </params>
    </zkaffold:object>

</site>
'''
        self.loginAsPortalOwner()

        self.portal.invokeFactory('Event', 'old-event', title='Old event')

        f = open(os.path.join(os.path.dirname(__file__), 'isotoma_logo.gif'))
        isotoma_logo_gif = f.read()
        f.close()

        self.context.readDataFile.side_effect = {
                'zkaffold/structure.xml': structure_xml,
                'zkaffold/images_dir/isotoma_logo.gif': isotoma_logo_gif,
                'zkaffold/files_dir/some-stuff.txt': 'some stuff\n',
                }.get

        import_site_structure(self.context)
        self.assert_('test-doc' in self.portal.objectIds())
        doc = self.portal['test-doc']
        self.assertEqual(doc.Title(), 'TEST')
        self.assertEqual(doc.getText().strip(), '<p>テスト</p>')
        self.assertTrue(doc.getExcludeFromNav())
        self.assertEqual(doc.getRelatedItems(), [
            self.portal.folder.collection,
            self.portal.event
            ])

        self.assert_('folder' in self.portal.objectIds())
        folder = self.portal.folder
        self.assertEqual(folder.Title(), 'folder')

        self.assert_('default-page' in folder.objectIds())
        default_page = folder['default-page']
        self.assertEqual(folder.getDefaultPage(), 'default-page')

        self.assert_('collection' in folder.objectIds())
        collection = folder.collection
        self.assertEqual(collection.Title(), 'Collection')
        self.assert_(collection.getCustomView())
        self.assertEqual(list(collection.getCustomViewFields()), [
            'title', 'CreationDate', 'review_state'])

        self.assert_('link' in folder.objectIds())
        link = folder.link
        self.assertEqual(link.Title(), 'Isotoma')
        self.assertEqual(link.getRemoteUrl(), 'http://www.isotoma.com/')

        self.assert_('downloads' in folder.objectIds())
        downloads = folder.downloads
        self.assertEqual(downloads.Title(), 'Downloads')

        self.assert_('some-stuff.txt' in downloads.objectIds())
        some_stuff = downloads['some-stuff.txt']
        self.assertEqual(some_stuff.Title(), 'Some stuff')
        self.assertEqual(some_stuff.getFile().data, 'some stuff\n')
        self.assertEqual(some_stuff.getFile().getFilename(), 'some-stuff.txt')

        self.assert_('isotoma_logo.gif' in downloads.objectIds())
        isotoma_logo = downloads['isotoma_logo.gif']
        self.assertEqual(isotoma_logo.Title(), 'Isotoma Logo')
        self.assertEqual(isotoma_logo.getImage().data, isotoma_logo_gif)
        self.assertEqual(isotoma_logo.getImage().getFilename(),
                'isotoma_logo.gif')

        self.assert_('event' in self.portal.objectIds())
        event = self.portal.event
        self.assertEqual(event.Title(), 'イベント')
        self.assertEqual(str(event.start()), '2010/01/01')
        self.assertEqual(str(event.end()), '2011/01/01')
        self.assertEqual(event.contact_name(), 'karen')
        self.assertEqual(event.contact_phone(), '1234')
        self.assertEqual(list(event.Subject()), [
            'plone'])

        self.assertEqual(self.portal['old-event'].Title(), 'modified title')

        self.assert_('news-item' in self.portal.objectIds())
        news_item = self.portal['news-item']
        self.assertEqual(news_item.Title(), 'News item')
        self.assertEqual(news_item.getImage().data, isotoma_logo_gif)
        self.assertEqual(news_item.getImage().getFilename(), 'isotoma_logo.gif')
        self.assertEqual(news_item.getImageCaption(), 'Image caption')

    def test_install_product(self):
        structure_xml = '''<?xml version="1.0" encoding="utf-8"?>
<site>
    <install product="plone.app.iterate" />
</site>
'''
        self.context.readDataFile.side_effect = {
                'zkaffold/structure.xml': structure_xml,
                }.get

        installer = self.portal.portal_quickinstaller
        import_site_structure(self.context)
        self.assert_(installer.isProductInstalled('plone.app.iterate'))

    def test_delete_content(self):
        structure_xml = '''<?xml version="1.0" encoding="utf-8"?>
<site>
    <delete id="my-page" portal_type="Document" />
    <delete id="type-doesnt-match" portal_type="File" />
</site>
'''
        self.context.readDataFile.side_effect = {
                'zkaffold/structure.xml': structure_xml,
                }.get

        self.loginAsPortalOwner()
        self.portal.invokeFactory('Document', 'my-page')
        self.portal.invokeFactory('Document', 'type-doesnt-match')

        import_site_structure(self.context)
        self.assert_('my-page' not in self.portal.objectIds())
        self.assert_('type-doesnt-match' in self.portal.objectIds())

    def test_apply_zope_interface(self):
        structure_xml = '''<?xml version="1.0" encoding="utf-8"?>
<site portal_id="%s" interfaces_path="zkaffold.exportimport.tests.test_exportimport">
    <Document id="my-page">
        <interfaces>
            <interface>ITestZkaffoldInterface</interface>
        </interfaces>
    </Document>
</site>
''' % self.portal.getId()
        self.context.readDataFile.side_effect = {
                'zkaffold/structure.xml': structure_xml,
                }.get

        self.loginAsPortalOwner()
        import_site_structure(self.context)
        self.assert_('my-page' in self.portal.objectIds())
        page = self.portal['my-page']

        self.assert_(ITestZkaffoldInterface.providedBy(page))

        structure_xml = '''<?xml version="1.0" encoding="utf-8"?>
<site portal_id="%s" interfaces_path="zkaffold.exportimport.tests.test_exportimport">
    <my-page>
        <modify>
            <interfaces>
                <remove>ITestZkaffoldInterface</remove>
            </interfaces>
        </modify>
    </my-page>
</site>
''' % self.portal.getId()

        self.context.readDataFile.side_effect = {
                'zkaffold/structure.xml': structure_xml,
                }.get

        import_site_structure(self.context)
        self.assert_(not ITestZkaffoldInterface.providedBy(page))

    def test_modify_content(self):
        self.loginAsPortalOwner()
        self.portal.invokeFactory('Document', 'test', title='Test Document')
        page = self.portal.test

        structure_xml = '''<?xml version="1.0" encoding="utf-8"?>
<site portal_id="%s">
    <test>
        <modify>
            <params>
                <param name="title" type="text">Modified by zkaffold</param>
            </params>
        </modify>
    </test>
</site>
''' % self.portal.getId()
        self.context.readDataFile.side_effect = {
                'zkaffold/structure.xml': structure_xml,
                }.get

        self.assertEqual(page.Title(), 'Test Document')
        import_site_structure(self.context)
        self.assertEqual(page.Title(), 'Modified by zkaffold')

    def test_publish(self):
        wf = self.portal.portal_workflow
        wf.setChainForPortalTypes(('Folder',), ('intranet_workflow',))
        structure_xml = '''<?xml version="1.0" encoding="utf-8"?>
<site>
    <Folder id="external" state="external">
        <params>
            <param name="title" type="text">External folder</param>
        </params>

        <Folder id="internal">
            <params>
                <param name="title" type="text">Internal folder</param>
            </params>
        </Folder>
    </Folder>
</site>
'''
        publish_xml = '''<?xml version="1.0" encoding="utf-8"?>
<transitions>
    <publish>
        <for>intranet_workflow</for>
        <steps>
            <step>publish_internally</step>
        </steps>
    </publish>
    <publish state="external">
        <for>intranet_workflow</for>
        <steps>
            <step>publish_internally</step>
            <step>publish_externally</step>
        </steps>
    </publish>
</transitions>
'''
        self.context.readDataFile.side_effect = {
                'zkaffold/structure.xml': structure_xml,
                'zkaffold/publish.xml': publish_xml,
                }.get
        self.loginAsPortalOwner()
        import_site_structure(self.context)

        self.assertEqual(wf.getInfoFor(self.portal.external.internal,
            'review_state'), 'internally_published')
        self.assertEqual(wf.getInfoFor(self.portal.external, 'review_state'),
                'external')

    def test_members(self):
        members_xml = '''<?xml version="1.0" encoding="utf-8"?>
<members>
    <member id="manager" password="password">
        <roles>
            <role>Manager</role>
        </roles>
        <memberdata>
            <item type="fullname">マネージャ</item>
            <item type="email">nobody@isotoma.com</item>
        </memberdata>
    </member>

    <member id="normal" password="password">
        <roles>
            <role>Editor</role>
            <role>Reviewer</role>
        </roles>
        <memberdata>
        </memberdata>
    </member>
</members>
'''
        self.context.readDataFile.side_effect = {
                'zkaffold/members.xml': members_xml,
                }.get

        import_site_structure(self.context)

        manager = self.portal.portal_membership.getMemberById('manager')
        self.assertEqual(sorted(manager.getRoles()),
                ['Authenticated', 'Manager'])
        self.assertEqual(manager.getProperty('fullname'), 'マネージャ')
        self.assertEqual(manager.getProperty('email'), 'nobody@isotoma.com')

        normal = self.portal.portal_membership.getMemberById('normal')
        self.assertEqual(sorted(normal.getRoles()),
                ['Authenticated', 'Editor', 'Reviewer'])


def test_suite():
    return unittest.makeSuite(TestImportSiteStructure)
