# -*- coding: utf-8 -*-
# $Id: test_contentexporter.py 7880 2010-10-19 13:34:34Z karen $

'''
test_contentexporter.py
-----------------------
Tests for content exporter
'''

__author__ = 'Karen Chan <karen@isotoma.com>'
__docformat__ = 'restructuredtext en'
__version__ = '$Revision: 7880 $'[11:-2]

import unittest

from lxml import etree

import mock

from Products.Five.utilities.interfaces import IMarkerInterfaces

from zkaffold import contentexporter
from zkaffold.tests import functional

TEST_MARKER_INTERFACE = ('Products.CMFPlone.interfaces.breadcrumbs.'
        'IHideFromBreadcrumbs')


class TestDefaultFieldExporters(functional.FunctionalTestCase):
    """Tests for the default field exporters
    """

    def afterSetUp(self):
        self.loginAsPortalOwner()

        self.portal.invokeFactory('Document', 'other-page')
        other_page = self.portal['other-page']

        self.portal.invokeFactory('Document', 'test')
        self.page = self.portal.test
        self.page.setTitle('テスト Document')
        self.page.setSubject(('test', 'document',))
        self.page.setExcludeFromNav(True)
        self.page.setRelatedItems([other_page])

        marker_interfaces = IMarkerInterfaces(self.page)
        marker_interfaces.update(
                add=marker_interfaces.dottedToInterfaces(
                    (TEST_MARKER_INTERFACE,)
                    ))

        self.exporter = self.portal.getSiteManager().queryUtility(
                contentexporter.IContentExporter)

    def test_unicode_field(self):
        param = contentexporter.unicode_field(self.page,
                self.page.getField('title'))
        self.assertEqual(param.tag, 'param')
        self.assertEqual(param.attrib, {
            'name': 'title',
            'type': 'text',
            })
        self.assertEqual(param.text, u'テスト Document')

    def test_list_field(self):
        param = contentexporter.list_field(self.page,
                self.page.getField('subject'))
        self.assertEqual(param.tag, 'param')
        self.assertEqual(param.attrib, {
            'name': 'subject',
            'type': 'list',
            })

        self.assertEqual(len(param.xpath('items')), 1)
        items = param.xpath('items')[0].xpath('item')
        self.assertEqual(len(items), 2)
        self.assertEqual(items[0].attrib, {
            'type': 'text',
            })
        self.assertEqual(items[0].text, 'test')
        self.assertEqual(items[1].attrib, {
            'type': 'text',
            })
        self.assertEqual(items[1].text, 'document')

    def test_reference_field(self):
        param = contentexporter.reference_field(self.page,
                self.page.getField('relatedItems'))
        self.assertEqual(param.tag, 'param')
        self.assertEqual(param.attrib, {
            'name': 'relatedItems',
            'type': 'reference_list',
            })

        self.assertEqual(len(param.xpath('items')), 1)
        items = param.xpath('items')[0].xpath('item')
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0].attrib, {
            'type': 'text',
            })
        self.assertEqual(items[0].text, '/other-page')

    def test_marker_interfaces(self):
        root = etree.Element('root')
        self.exporter.export_interfaces(self.page, root)
        self.assertEqual(len(root), 1)
        self.assertEqual(root[0].tag, 'interfaces')
        interfaces = root[0]
        self.assertEqual(len(interfaces), 1)
        self.assertEqual(interfaces[0].tag, 'interface')
        self.assertEqual(interfaces[0].text, TEST_MARKER_INTERFACE)


class TestContentExporter(unittest.TestCase):
    pass


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestDefaultFieldExporters))
    suite.addTest(unittest.makeSuite(TestContentExporter))
    return suite
