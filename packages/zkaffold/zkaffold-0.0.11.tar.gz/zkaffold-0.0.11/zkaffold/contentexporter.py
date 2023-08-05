# $Id$

'''
contentexporter.py
------------------
Export a plone site into a zkaffold structure xml file.
'''

__author__ = 'Karen Chan <karen.chan@isotoma.com>'
__docformat__ = 'restructuredtext en'
__version__ = '$Revision$'[11:-2]

import sys

from lxml import etree

from Acquisition import aq_base
from Products.Five.utilities.interfaces import IMarkerInterfaces
from zope.interface import Interface, implements

from config import ZKAFFOLD_NAMESPACE


def unicode_field(plone_object, field):
    if not field.get(plone_object):
        return
    if field.get(plone_object) == field.default:
        return
    param = etree.Element('param', name=field.getName(), type='text')
    param.text = etree.CDATA(unicode(field.get(plone_object), 'utf-8'))
    return param

def text_field(plone_object, field):
    if not field.get(plone_object):
        return
    if field.get(plone_object) == field.default:
        return
    param = etree.Element('param', name=field.getName(), type='text')
    param.text = str(field.get(plone_object))
    return param

def boolean_field(plone_object, field):
    if field.get(plone_object) is None:
        return
    if (field.get(plone_object) == field.default or
            field.default is None and field.get(plone_object) is False):
        return
    param = etree.Element('param', name=field.getName(), type="boolean")
    param.text = str(field.get(plone_object))
    return param

def list_field(plone_object, field):
    if not field.get(plone_object):
        return
    if field.get(plone_object) == field.default:
        return
    param = etree.Element('param', name=field.getName(), type='list')
    items = etree.SubElement(param, 'items')
    for i in field.get(plone_object):
        item = etree.SubElement(items, 'item', type='text')
        item.text = unicode(i, 'utf-8')
    return param

def reference_field(plone_object, field):
    references = field.get(plone_object)
    if not references:
        return
    param = etree.Element('param', name=field.getName())
    if not isinstance(references, list):
        if not references:
            return
        # returns the path without '/portal'
        param.attrib['type'] = 'reference'
        param.text = '/%s' % '/'.join(references.getPhysicalPath()[2:])
        return param
    param.attrib['type'] = 'reference_list'
    items = etree.SubElement(param, 'items')
    for ref in references:
        if not ref:
            continue
        item = etree.SubElement(items, 'item', type='text')
        item.text = '/%s' % '/'.join(ref.getPhysicalPath()[2:])
    return param

def datetime_field(plone_object, field):
    param = etree.Element('param', name=field.getName(), type='date')
    value = field.get(plone_object)
    if field.get(plone_object) == field.default:
        return
    if value:
        param.text = str(value)
        return param

def default_filename(plone_object, field):
    """Returns a default filename for a plone_object and field.
    """
    return '%s-%s' % (
            '-'.join(plone_object.getPhysicalPath()[2:]),
            field.getName())

def image_field(plone_object, field):
    param = etree.Element('param', name=field.getName(), type='image')
    value = field.get(plone_object)
    if field.get(plone_object) == field.default:
        return
    if value and value.data:
        filename = field.get(plone_object).filename
        if not filename:
            filename = default_filename(plone_object, field)
        param.text = filename
        return (param, filename, value.data)

def file_field(plone_object, field):
    param = etree.Element('param', name=field.getName(), type='file')
    value = field.get(plone_object)
    if field.get(plone_object) == field.default:
        return
    if value and value.data:
        filename = field.get(plone_object).filename
        if not filename:
            filename = default_filename(plone_object, field)
        param.text = filename
        return (param, filename, value.data)


class IContentExporter(Interface):
    """Export a plone site into a zkaffold structure xml file.
    """


_mod = 'zkaffold.contentexporter'
_default_exporters = {
        'Products.Archetypes.Field.StringField': '%s.unicode_field' % _mod,
        'Products.Archetypes.Field.TextField': '%s.unicode_field' % _mod,
        'Products.Archetypes.Field.IntegerField': '%s.text_field' % _mod,
        'Products.Archetypes.Field.BooleanField': '%s.boolean_field' % _mod,
        'Products.Archetypes.Field.DateTimeField': '%s.datetime_field' % _mod,
        'Products.Archetypes.Field.LinesField': '%s.list_field' % _mod,
        'Products.Archetypes.Field.ReferenceField': '%s.reference_field' % _mod,
        'Products.OrderableReferenceField._field.OrderableReferenceField': (
            '%s.reference_field' % _mod),
        'plone.app.blob.subtypes.image.ExtensionBlobField':
                '%s.image_field' % _mod,
        'Products.Archetypes.Field.ImageField': '%s.image_field' % _mod,
        'plone.app.blob.subtypes.file.ExtensionBlobField':
                '%s.file_field' % _mod,
        'Products.Archetypes.Field.FileField': '%s.file_field' % _mod,
        }


class ContentExporter(object):
    """Export a plone site into a zkaffold structure xml file.
    """

    implements(IContentExporter)

    def __init__(self):
        self.files = {}

        self.logger = None

        # exporters for different fields
        self._field_exporters = {}
        for field, func in _default_exporters.items():
            self.register_field_exporter(field, func)

        # fields that are not going to be in params
        self.exclude_params = [
                'id',
                'creation_date',
                'language',
                'creators',
                'modification_date',
                'locallyAllowedTypes',
                'immediatelyAddableTypes',
                'constrainTypesMode',
                ]

    def register_field_exporter(self, field_type, function):
        """Registers a exporter function for a field type.

        :Parameters:
          - `field_type`: a str that contains the name of the class, e.g.
            Products.Archetypes.Field.StringField
          - `function`: str, function that takes plone_object and field as
            arguments and returns a lxml.etree.Element for the <param> tag or
            (lxml.etree.Element, filename, file content)
        """
        self._field_exporters[field_type] = function.rsplit('.', 1)

    def get_field_exporter(self, field_type):
        """Returns an exporter function for a field type, if there is
        no exporter registered for a field, returns the exporter
        function text_field.

        :Parameters:
          - `field_type`: a str that contains the name of the class,
            e.g. Products.Archetypes.Field.StringField
        :Returns: a function for exporting the field
        """
        if field_type not in self._field_exporters:
            if self.logger:
                self.logger.warning('%s has no registered exporter.' % field_type)
        mod, func = self._field_exporters.get(field_type, (_mod, 'text_field'))
        if mod not in sys.modules:
            __import__(mod)
        return getattr(sys.modules[mod], func)

    def export_attributes(self, plone_object, root):
        """Export the attributes of a plone object into zkaffold xml.

        :Parameters:
          - `plone_object`: An object in a plone site
          - `root`: The root lxml.etree.Element object that represents the
                    plone_object in the xml
        """
        params = etree.Element('params')
        for name in plone_object.Schema().keys():
            if name in self.exclude_params:
                continue
            field = plone_object.getField(name)
            exporter = self.get_field_exporter(field.getType())
            param = exporter(plone_object, field)
            if param is not None:
                if isinstance(param, tuple):
                    param, filename, file_content = param
                    self.files[filename] = file_content
                params.append(param)
        if len(params) > 0:
            root.append(params)

    def export_interfaces(self, plone_obj, root):
        """Export marker interfaces that a plone object has.

        :Parameters:
          - `plone_object`: An object in a plone site
          - `root`: The root lxml.etree.Element object that represents the
                    plone_object in the xml
        """
        interfaces = IMarkerInterfaces(plone_obj).getDirectlyProvidedNames()
        if interfaces:
            elem = etree.SubElement(root, 'interfaces')
            for interface in interfaces:
                interface_elem = etree.SubElement(elem, 'interface')
                interface_elem.text = interface

    def export_plone_object(self, plone_object, root):
        """Export a plone object into zkaffold xml.

        :Parameters:
          - `plone_object`: An object in a plone site
          - `root`: The root lxml.etree.Element object that represents the
                    plone_object in the xml
        """
        default_page = plone_object.getDefaultPage()
        for id in plone_object.objectIds():
            child_obj = getattr(plone_object, id)
            child_base_obj = aq_base(child_obj)
            if (hasattr(child_base_obj, 'portal_type') and
                    hasattr(child_base_obj, 'schema')):
                # We only care about objects that have portal_type
                # tools don't have it, and tools won't be included in the xml
                if ' ' in child_obj.portal_type:
                    child = etree.SubElement(root,
                            '{%s}object' % ZKAFFOLD_NAMESPACE,
                            portal_type=child_obj.portal_type, id=id)
                else:
                    child = etree.SubElement(root,
                            child_obj.portal_type, id=id)
                if id == default_page:
                    child.set('is_default_page', 'True')
                self.export_attributes(child_obj, child)
                self.export_interfaces(child_obj, child)
                self.export_plone_object(child_obj, child)

    def export_site_structure(self, plone_site, logger=None):
        """Export a plone site into a zkaffold structure xml.

        :Parameters:
          - `plone_site`: A plone site
          - `logger`: for logging warnings and errors
        :Returns: (a xml string, dict {filename => file content, ...})
        """
        self.files = {}
        if logger:
            self.logger = logger
        root = etree.Element('site', nsmap={'zkaffold': ZKAFFOLD_NAMESPACE})
        self.export_plone_object(plone_site, root)
        return etree.tostring(root, pretty_print=True, encoding='utf-8'), self.files
