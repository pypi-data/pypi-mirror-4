# $Id: contentimporter.py 9409 2011-02-14 13:18:33Z antony $

__author__ = 'Pat Smith <pat@isotoma.com>'
__docformat__ = 'restructuredtext en'
__version__ = '$Revision: 9409 $'[11:-2]

import os
import logging
from lxml import etree as ElementTree

from zope.interface import directlyProvides, directlyProvidedBy

from DateTime import DateTime
from Products.Five.utilities.interfaces import IMarkerInterfaces
from Products.Archetypes.utils import shasattr
from Products.CMFCore.utils import getToolByName

from Products.CMFCore.WorkflowTool import WorkflowException
from Products.Archetypes.exceptions import ReferenceException

from wordy import WordSmith
from config import ZKAFFOLD_NAMESPACE

try:
    # Ensure LinguaPlone patches are applied if possible
    import Products.LinguaPlone
except ImportError:
    # no LinguaPlone
    pass

latin = os.path.join(os.path.dirname(__file__), 'latinwords')
ws = WordSmith(wordfile=latin)

def _loadFile(file_dir, filename):
    file = os.path.join(file_dir, filename)
    return open(file).read()


class ContentImporter:

    def __init__(self, importSource='testcontent.xml', content_dir='content',
            content_xml='', publish_xml='', load_file=None):
        """Import content from xml.

        :Parameters:
          - `importSource`: filenme of the content xml file
          - `content_dir`: path to the directory that contains the
            content xml file, image / file directories etc
          - `content_xml`: the content of the content xml file, if given
            importSource will not be used.
          - `publish_xml`: the content of the publish xml file
          - `load_file`: a function that gets passed in the file directory and
            filename and returns the content of the file
        """
        self.contentfile = os.path.join(content_dir, importSource)
        if content_xml:
            self.root = ElementTree.fromstring(content_xml)
        else:
            tree = ElementTree.ElementTree(file=self.contentfile)
            self.root = tree.getroot()
        self.image_dir = os.path.join(content_dir, self.root.get('image_dir', ''))
        self.file_dir = os.path.join(content_dir, self.root.get('file_dir', ''))
        self.interfaces_path = self.root.get('interfaces_path', '')
        self.current_element = None
        self.logger = logging.getLogger('ContentImporter')

        self.transitions = {}
        if publish_xml:
            self.transitions = self._parse_publish_xml(publish_xml)

        if load_file is None:
            self._loadFile = _loadFile
        else:
            self._loadFile = load_file

        if self.interfaces_path:
            self.interfaces_module = __import__(self.interfaces_path, {}, {}, ['*'])
        else:
            self.interfaces_module = None

        # for storing how to publish items that need special transition or end state
        self._publish_states = {}
        self._publish_items = []

    def _parse_publish_xml(self, publish_xml):
        """Parse publish.xml into a dict {publish state: {workflow id:
        [transitions], ...}, ...}

        :Parameters:
          - `publish_xml`: str, content of publish.xml
        :Returns: a dict from publish state to workflow id to transitions id to
                  publish an object with that workflow
        """
        root = ElementTree.fromstring(publish_xml)
        transitions = {}
        for publish in root.xpath('/transitions/publish'):
            transition = transitions.setdefault(unicode(publish.get('state',
                'published')), {})
            steps = []
            for step in publish.xpath('steps/step/text()'):
                steps.append(unicode(step))
            for workflow in publish.xpath('for/text()'):
                transition[unicode(workflow)] = steps
        return transitions

    def _missingFields(self, context, portal_type, given_fields):
        pt = getToolByName(context, 'portal_types')
        at = getToolByName(context, 'archetype_tool')
        required_fields = []

        fti = pt.get(portal_type)
        if fti:
            type = at.lookupType(fti.product, portal_type)
            if type:
                not_reference = lambda f:f.type!='reference'
                no_usable_default = lambda f:f.type!='boolean' and not bool(f.default)
                required_fields = [f.getName() for f in type['schema'].filterFields(not_reference, no_usable_default, required=True)]

        missing_fields = [f for f in required_fields if f not in given_fields and f != 'id']
        return missing_fields

    def publish(self, obj, transition='publish', state='published'):
        """Publish a plone object.  If transition cannot be used to publish the
        object, look for transition information in publish.xml.

        :Parameters:
          - `obj`: an object in the plone site
          - `transition`: the workflow transition id to publish the plone object
          - `state`: str, a different end state as defined in publish.xml
        """
        wf = getToolByName(obj, 'portal_workflow')
        workflows = wf.getChainFor(obj)
        if not workflows:
            return

        try:
            wf.doActionFor(obj, transition)
            return
        except WorkflowException:
            pass

        workflow = workflows[0]
        if (state not in self.transitions or
                workflow not in self.transitions[state]):
            self.logger.log(logging.WARNING,
                    "Can't publish %s" % (
                        '/'.join(obj.getPhysicalPath())))
            return

        for transition in self.transitions[state][workflow]:
            try:
                wf.doActionFor(obj, transition)
            except WorkflowException:
                self.logger.log(logging.WARNING,
                        "Can't publish %s" % (
                            '/'.join(obj.getPhysicalPath())))
                return

    def _createItem(self, parent, portal_type, id, properties={},
            transition='publish', state='published'):
        """ Add an item """
        pt = getToolByName(parent, 'portal_types')

        missing_fields = self._missingFields(parent, portal_type,
                                             properties.keys())
        if missing_fields:
            raise RuntimeError, "Missing required fields: %s for %s at %s\n\t%s, line %d" % (', '.join(missing_fields), portal_type, '/'.join(parent.getPhysicalPath()+(id,)), self.contentfile, self.current_element.sourceline)

        pt.constructContent(portal_type, parent, id, None)
        ob = parent.get(id)
        self._modifyItem(ob, properties)
        fti = pt.getTypeInfo(portal_type)
        if hasattr(fti, '_finishConstruction'):
            fti._finishConstruction(ob)
        if shasattr(ob, 'at_post_create_script'):
            ob.unmarkCreationFlag()
            ob.at_post_create_script()
        if transition != 'publish' or state != 'published':
            self._publish_states[ob.getPhysicalPath()] = (transition, state)
        return ob

    def _modifyItem(self, item, properties={}):
        """ Modify an item """
        for k,v in properties.items():
            field = item.getField(k)
            if field:
                field.set(item, v)
            else:
                self.logger.log(logging.WARNING,
                        '"%s" does not have field "%s"' % (item.getId(), k))
        return item

    def _modifyRefs(self, item, references, reftype):
        """ Modify references """
        for k,v in references.items():
            item.deleteReference(reftype)
            item.addReference(v,reftype)
        return item

    def _deleteItem(self, parent, id, ctype=None, portal_type=None):
        if id in parent.objectIds():
            item = parent[id]
            if (ctype is None and portal_type is None or
                    item.meta_type == ctype or
                    item.portal_type == portal_type):
                parent.manage_delObjects(id)

    def _setInterfaces(self, ob, interfaces, removelist=[]):
        if interfaces and len(interfaces):
            directlyProvides(ob, interfaces)
        for interface in removelist:
            if interface.providedBy(ob):
                directlyProvides(ob, directlyProvidedBy(ob) - interface)

    def _getLoremIpsum(self, paracount=3):
        if paracount is None:
            paracount = 3
        else:
            paracount = int(paracount)
        return ws(paracount)

    def _getItems(self, listelem):
        itemselement = listelem.find('items')
        if itemselement is None:
            return None
        items = []
        itemslist = itemselement.findall('item')
        for i in itemslist:
            itype = i.get('type')
            if itype == "text":
                items.append(i.text)
            elif itype == "reference_list":
                items.append(i.text)
            elif itype == "reference":
                items.append(i.text)
            else:
                raise RuntimeError, "Unknown XML setup item type: %s" % (itype)
        return items

    def _getElementParams(self, elem):
        paramselement = elem.find('params')
        if paramselement is None:
            return {}
        params = {}
        paramslist = paramselement.findall('param')
        for p in paramslist:
            ptype = p.get('type')
            pname = p.get('name')

            if ptype == "text":
                params[pname] = p.text
            elif ptype == "file":
                params[pname] = (self._loadFile(self.file_dir, p.text.strip()),
                        p.text.strip())
            elif ptype == "image":
                params[pname] = (self._loadFile(self.image_dir,
                    p.text.strip()), p.text.strip())
            elif ptype == "loremipsum":
                params[pname] = "\n\n".join(self._getLoremIpsum(p.get("paras")))
            elif ptype == "loremipsum_html":
                content = ""
                for p in self._getLoremIpsum(p.get("paras")):
                    content += "<p>%s</p>" % (p)
                params[pname] = content
            elif ptype == "loremipsum_sentence":
                params[pname] = ws._getsentence()
            elif ptype == "boolean":
                try:
                    params[pname] = (bool(int(p.text)) == True)
                except ValueError:
                    if p.text.strip().lower() == 'true':
                        params[pname] = True
                    else:
                        params[pname] = False
            elif ptype == "list":
                params[pname] = self._getItems(p)
            elif ptype == "date":
                if p.text == "now" or "":
                    params[pname] = DateTime()
                else:
                    params[pname] = DateTime(p.text)
            elif ptype == "reference":
                pass
            elif ptype == "reference_list":
                pass
            else:
                raise RuntimeError, "Unknown XML setup param type: %s" % (ptype)
        return params

    def _import(self, path):
        """Helper function for importing dynamic paths.

        :Parameters:
          - `path`: str of path to import, e.g. "zkaffold.contentimport.ContentImporter"
        :Returns: the imported object will be returned.  Using the same
                  example, ContentImporter will be returned
        """
        if '.' not in path:
            return __import__(path)
        module, obj = path.rsplit('.', 1)
        module = __import__(module, {}, {}, ['*'])
        return getattr(module, obj)

    def _getElementInterfaces(self, elem):
        ielems = elem.find('interfaces')
        if ielems is None:
            return (None, [])
        interfaceslist = ielems.findall('interface')
        interfaceslist = [el.text for el in interfaceslist]
        interfaces = []
        for comp in interfaceslist:
            try:
                iface = getattr(self.interfaces_module, comp)
            except AttributeError:
                iface = self._import(comp)
                if not iface:
                    raise ImportError, "Could not import %s from %s" % (comp, self.interfaces_path)
            interfaces.append(iface)
        removelist = []
        for interface in [el.text for el in ielems.findall('remove')]:
            try:
                iface = getattr(self.interfaces_module, interface)
            except AttributeError:
                iface = self._import(interface)
                if not iface:
                    raise ImportError, "Could not import %s from %s" % (comp, self.interfaces_path)
            removelist.append(iface)
        return (interfaces, removelist)

    def _getElementReferences(self, elem):
        paramselement = elem.find('params')
        if paramselement is None:
            return None
        params = {}
        paramslist = paramselement.findall('param')
        for p in paramslist:
            ptype = p.get('type')
            pname = p.get('name')

            if ptype == "reference":
                preftype = p.get('reftype')
                params[pname] = (p.text, preftype)

        return params

    def _getElementReferenceLists(self, elem):
        paramselement = elem.find('params')
        if paramselement is None:
            return None
        params = {}
        paramslist = paramselement.findall('param')
        for p in paramslist:
            ptype = p.get('type')
            pname = p.get('name')

            if ptype == "reference_list":
                preftype = p.get('reftype')
                params[pname] = (self._getItems(p), preftype)

        return params

    def importContent(self, portal):
        print "\n= Importing =================================================="
        print "%s:" % (self.contentfile)
        factory = portal.manage_addProduct['CMFPlone']
        qi = getToolByName(portal, 'portal_quickinstaller')
        def createContent(elem, parent=portal):
            self.current_element = elem
            if type(elem) == ElementTree._Comment:
                return
            t = elem.tag
            id = elem.get('id')
            # Traverse where element's tag matches an existing ZODB object

            f = None
            if t in parent.objectIds():
                f = getattr(parent, t)
            elif elem == self.root:
                f = parent

            params = {}
            filenames = {}
            results = self._getElementParams(elem)
            for p in results:
                if isinstance(results[p], tuple):
                    (value, filename) = results[p]
                    params[p] = value
                    filenames[p] = filename
                else:
                    params[p] = results[p]
            (interfaces, removelist) = self._getElementInterfaces(elem)
            if t == 'modify':
                if params:
                    self._modifyItem(parent, params)
                if interfaces or removelist:
                    self._setInterfaces(parent, interfaces, removelist)
                return parent
            elif t == 'delete':
                ctype = elem.get('ctype')
                self._deleteItem(parent, id, ctype, portal_type=elem.get('portal_type'))
                return None
            elif t == 'install':
                product = elem.get('product')
                qi.installProducts([product,])
                return None
            else:
                if id is not None:
                    # Tag designed especially for portal types with spaces:
                    #
                    # <zkaffold:object xmlns:zkaffold="http://www.isotoma.com/zkaffold">
                    #     <params>
                    #         ...
                    #     </params>
                    # </zkaffold:object>
                    if t == '{%s}object' % ZKAFFOLD_NAMESPACE:
                        t = elem.get('portal_type')
                    print "> %-20s %-20s in %s" % (t[0:20], id[0:20], parent)
                    f = self._createItem(parent, t, id, params or {}, state=elem.get('state', 'published'))
                    self._publish_items.append(f)
                    for field in filenames:
                        f.getField(field).get(f).setFilename(filenames[field])
                    self._setInterfaces(f, interfaces, removelist)
                    if elem.get('is_default_page',None):
                        parent.setDefaultPage(id)
                if not f:
                    self.logger.log(logging.WARNING, 'Missing content item or ID attribute, "%s".' % t)
                else:
                    for child in elem:
                        if child.tag != 'params' and child.tag !='interfaces':
                            child_result = createContent(child, f)
                            if child_result:
                                child_result.reindexObject()

                return f or parent
        try:
            root_result = createContent(self.root)
        except Exception, e:
            at_element = hasattr(self.current_element, 'tag') and ('at element "%s" ' % self.current_element.tag) or ''
            self.logger.log(logging.ERROR, 'Error %son line %d of %s when creating content.' % (at_element, self.current_element.sourceline, self.contentfile))
            raise
        if root_result:
            root_result.reindexObject()
        print "\n= Adding references =========================================="

        def objToStr(obj):
            return '<%s at %s>' % (obj.portal_type, obj.getId())

        def getApp(obj):
            """Returns the Application object of obj.
            """
            while not obj.isTopLevelPrincipiaApplicationObject:
                obj = obj.getParentNode()
            return obj

        def getBrains(portal, path):
            """Returns the plone brains with path path

            :Parameters:
              - `portal`: portal object
              - `path`: str, path to the object without portal id
            """
            app = getApp(portal)
            path = "%s%s" % (portal.absolute_url()[len(app.absolute_url()):], path)
            return portal.portal_catalog({'path': path, 'Language': 'all'})

        def createReferences(elem, obj=portal):
            self.current_element = elem
            if type(elem) == ElementTree._Comment:
                return
            t = elem.tag
            id = elem.get('id')

            # Allow for an attribute 'setDefaultPage' on the modify tag that
            # will... set the default page of a folderish type.
            if t == 'modify':
                default_page = elem.get('setDefaultPage', None)
                if default_page:
                    obj.setDefaultPage(default_page)
                    obj.reindexObject()
            params = self._getElementReferences(elem)
            try:
                f = getattr(obj, t)
            except AttributeError, e:
                if id:
                    f = obj.get(id)
                else:
                    f = obj

            if params:
                if id:
                    obj = obj.get(id)

                for k, (v, reftype) in params.items():
                    references = []
                    reference = None
                    brains = getBrains(portal, v)
                    if brains:
                        uid = brains[0]['UID']
                        print "> %-20s %-20s in %s" % ("Adding reference to", v.split('/')[-1][0:20], objToStr(obj))
                        reference = uid
                    else:
                        print "WARNING: cannot locate item at %s in %s\n" % (v,objToStr(obj))

                    if reference:
                        if reftype!=None:
                            f = self._modifyRefs(obj, {k: reference}, reftype)
                        else:
                            f = self._modifyItem(obj, {k: reference})
                        obj.reindexObject()

            for child in elem:
                if child.tag != 'params':
                    createReferences(child, f)
        try:
            createReferences(self.root)
        except Exception, e:
            at_element = hasattr(self.current_element, 'tag') and ('at element "%s" ' % self.current_element.tag) or ''
            self.logger.log(logging.ERROR, 'Error %son line %d of %s when creating references.' % (at_element, self.current_element.sourceline, self.contentfile))
            raise

        def createReferenceLists(elem, obj=portal):
            self.current_element = elem
            if type(elem) == ElementTree._Comment:
                return
            t = elem.tag
            id = elem.get('id')
            params = self._getElementReferenceLists(elem)
            try:
                f = getattr(obj, t)
            except AttributeError, e:
                if id:
                    f = obj.get(id)
                else:
                    f = obj

            if params:
                if id:
                    obj = obj.get(id)

                for k, (v, reftype) in params.items():
                    references = []
                    for p in v:
                        brains = getBrains(portal, p)
                        if brains:
                            uid = brains[0]['UID']
                            print "> %-20s %-20s in %s" % ("Adding reference to", p.split('/')[-1][0:20], objToStr(obj))
                            references.append(uid)
                        else:
                            print "WARNING: cannot locate item at %s\n" % p

                    if len(references):
                        if obj.getField(k).multiValued:
                            if reftype!=None:
                                f = self._modifyRefs(obj, {k: references}, reftype)
                            else:
                                f = self._modifyItem(obj, {k: references})
                        else:
                            print "WARNING: %s is not multiValued, using first value only\n" % k
                            if reftype!=None:
                                f = self._modifyRefs(obj, {k: references[0]}, reftype)
                            else:
                                f = self._modifyItem(obj, {k: references[0]})
                        obj.reindexObject()

            for child in elem:
                if child.tag != 'params':
                    createReferenceLists(child, f)
        try:
            createReferenceLists(self.root)
        except Exception, e:
            at_element = hasattr(self.current_element, 'tag') and ('at element "%s" ' % self.current_element.tag) or ''
            self.logger.log(logging.ERROR, 'Error %son line %d of %s when creating reference lists.' % (at_element, self.current_element.sourceline, self.contentfile))
            raise e
        print "=Publishing site==============================================\n"
        for item in self._publish_items:
            transition, state = self._publish_states.get(item.getPhysicalPath(),
                    (None, None))
            if transition and state:
                self.publish(item, transition=transition, state=state)
            else:
                self.publish(item)
        print "==============================================================\n"
