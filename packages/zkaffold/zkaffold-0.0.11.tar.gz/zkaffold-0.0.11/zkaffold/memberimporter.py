# $Id: memberimporter.py 1136 2008-03-06 14:28:48Z pat $

__author__ = 'Pat Smith <pat@isotoma.com>'
__docformat__ = 'restructuredtext en'
__version__ = '$Revision: 1136 $'[11:-2]

import os
from lxml import etree as ElementTree

from DateTime import DateTime

from Products.Archetypes.utils import shasattr
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.WorkflowTool import WorkflowException

class MemberImporter:
    
    def __init__(self, importSource='members.xml', members_xml='',
            content_dir='content'):
        """Member importer

        :Parameters:
          - `importSource`: filename of the members xml.
          - `members_xml`: content of the members xml file, if used,
            importSource is ignored.
          - `content_dir`: the directory that contains the members xml file.
        """
        if members_xml:
            self.root = ElementTree.fromstring(members_xml)
        else:
            memberfile = os.path.join(content_dir, importSource)
            tree = ElementTree.ElementTree(file=memberfile)
            self.root = tree.getroot()
        self.with_membrane = bool(self.root.get('membrane', False))
        if self.with_membrane:
            self.default_member_type = self.root.get('default_member_type')

    def _getMemberData(self, elem):
        paramselement = elem.find('memberdata')
        md = {}
        for item in paramselement.findall('item'):
            md.update({item.get('type'):item.text})
        return md    
    
    def _getMemberRoles(self, elem):
        paramselement = elem.find('roles')
        if not paramselement:
            return []
        return [i.text for i in paramselement.findall('role')]

    def _getMemberGroups(self, elem):
        paramselement = elem.find('groups')
        if not paramselement:
            return []
        return [i.text for i in paramselement.findall('group')]
   
    def importMembers(self, portal):
        print "\n= Importing Members =========================================="
        pm = portal.portal_membership
        pg = portal.portal_groups
        mdc = getToolByName(portal, 'portal_memberdata')
        fac = getToolByName(portal, 'portal_factory')
        for elem in self.root:
            if type(elem) == ElementTree._Comment:
                pass
            elif elem.tag == 'member':
                id = elem.get('id')
                pwd = elem.get('password')
                roles = self._getMemberRoles(elem)
                md = self._getMemberData(elem)
                print "%s %s %s" %(id, md, roles)
                if self.with_membrane:
                    mem = mdc.restrictedTraverse('portal_factory/%s/%s' % (self.default_member_type, id))
                    user = fac.doCreate(mem, id)
                    md['roles'] = roles
                    md['password'] = pwd
                    md['confirm_password'] = pwd
                    user.processForm(values=md)
                else:
                    pm.addMember(id, pwd, [], [], md)
                    user = pm.getMemberById(id)
                    user.setSecurityProfile(password=pwd, roles=roles)
                    for group in self._getMemberGroups(elem):
                        pg.getGroupById(group).addMember(id)
        print "==============================================================\n"
