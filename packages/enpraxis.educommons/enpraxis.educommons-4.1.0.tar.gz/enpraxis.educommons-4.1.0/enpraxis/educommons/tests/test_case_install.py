##################################################################################
#    Copyright (c) 2004-2009 Utah State University, All rights reserved. 
#    Portions copyright 2009 Massachusetts Institute of Technology, All rights reserved.
#                                                                                 
#    This program is free software; you can redistribute it and/or modify         
#    it under the terms of the GNU General Public License as published by         
#    the Free Software Foundation, version 2.                                      
#                                                                                 
#    This program is distributed in the hope that it will be useful,              
#    but WITHOUT ANY WARRANTY; without even the implied warranty of               
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the                
#    GNU General Public License for more details.                                 
#                                                                                 
#    You should have received a copy of the GNU General Public License            
#    along with this program; if not, write to the Free Software                  
#    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA    
#                                                                                 
##################################################################################

__author__  = '''Brent Lambert, David Ray, Jon Thomas'''
__version__   = '$ Revision 0.0 $'[11:-2]

from base import eduCommonsTestCase
from Products.CMFCore.utils import getToolByName

class testInstall(eduCommonsTestCase):

   
    def test_eduCommonsInstall(self):
        self.failUnless('enpraxis.educommons' in [product['product'] for product in self.portal.portal_setup.listProfileInfo()])

    def test_installSiteType(self):
        site_type = self.portal.portal_types.getTypeInfo('Plone Site')
        self.failUnless(site_type.allowed_content_types)
        self.failUnless(site_type.filter_content_types)

    def test_installMembership(self):
        pm = self.portal.portal_membership
        self.failIf(pm.getMemberareaCreationFlag())

    def test_installDefaultContent(self):
        self.failIf(hasattr(self.portal,'Members'))
        self.failIf(hasattr(self.portal,'news'))
        self.failIf(hasattr(self.portal,'events'))

    def test_installSyndication(self):
        self.failUnless(hasattr(self.portal,'syndication_information'))

    def test_installRoles(self):
        role_ids = [rl for rl in self.portal.acl_users.portal_role_manager.listRoleIds()]
        roles = ['Producer','QA','Publisher','Viewer','Administrator']
        for role in roles:
            self.failUnless(role in role_ids)

    def test_installControlPanel(self):
        control_panel = getToolByName(self.portal, 'portal_controlpanel', None)
        las = ['ContentLicensing','ZipFileTransport','bookmarklets','LeftSkin_basic', 'LeftSkin_adv', 'LeftSkin_compl', 'eduCommons']
        for la in las:
            self.failUnless(la in [listAction.id for listAction in control_panel.listActions()])
               
    def test_installDefaultObjects(self):
        actions = getToolByName(self.portal, 'portal_actions', None)
        las =  ['syllabus_view','schedule_view','aboutprof_view','frontpage_view','abouttext_view','tou_view','faq_view','privacypolicy_view','division_view','course_view']
        for la in las:
            self.failUnless(la in [listAction.id for listAction in actions.listActions()])

    def test_installJavascriptObjects(self):
        pjs = getToolByName(self.portal, 'portal_javascripts',None)
        self.failIf(pjs.getResource('mark_special_links.js').getEnabled())

    def test_installIndexes(self):
        pc = getToolByName(self.portal, 'portal_catalog')
        indices = ['getCourseId','getTerm','getInstructorName']
        for index in indices:
            self.failUnless(index in pc.indexes())

    def test_installWorflows(self):
        wtool = self.portal.portal_workflow
        self.failUnless('content_workflow' in wtool.listWorkflows())

    def test_installSiteProperties(self):
        props = getattr(self.portal.portal_properties, 'site_properties')
        self.assertEqual(props.localTimeFormat,'%m-%d-%Y')
        self.assertEqual(props.ext_editor,0)
        typesInListings = list(props.typesUseViewActionInListings)
        typesInListings.sort()
        self.assertEqual(props.disable_folder_sections,0)

    def test_installSiteCSS(self):
        cssreg = getToolByName(self.portal,'portal_css')
        ecss = cssreg.getResource('eduCommonsContent.css')
        self.assertEqual(ecss.getCookable(),True)

    def test_installFeedback(self):
        assert self.portal.feedback.title == 'Feedback', 'Feedback title has not been set.'
               
def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(testInstall))
    return suite


