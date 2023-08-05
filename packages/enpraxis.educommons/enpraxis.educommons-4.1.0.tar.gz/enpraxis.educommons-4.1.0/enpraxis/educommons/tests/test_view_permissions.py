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

"""Object editing testing module"""

import sys
from unittest import TestSuite, makeSuite
from zope.annotation.interfaces import IAnnotations
from AccessControl.SecurityManager import setSecurityPolicy
from Products.CMFCore.utils import _checkPermission as checkPerm
from AccessControl import ZopeGuards
from AccessControl.ZopeGuards import guarded_getattr, get_safe_globals
from AccessControl.ImplPython import ZopeSecurityPolicy
from AccessControl import Unauthorized

from Products.CMFCore.permissions import AccessContentsInformation
from Products.CMFCore.permissions import View
from Products.CMFCore.permissions import ModifyPortalContent

from Products.CMFCore.permissions import View
from Acquisition import aq_base

from Testing.ZopeTestCase import user_name

# Restricted Python imports
from RestrictedPython import compile_restricted
from RestrictedPython.Guards import safe_builtins
from RestrictedPython.SafeMapping import SafeMapping

from base import eduCommonsTestCase

class TestEditing(eduCommonsTestCase):
    """Test object editing for different roles and workflow states"""

    def afterSetUp(self):
        self.catalog = self.portal.portal_catalog
        self.workflow = self.portal.portal_workflow
        self.membership = self.portal.portal_membership

        setSecurityPolicy(ZopeSecurityPolicy(verbose=True))

        # We need to manually register the roles from the rolemap with
        # the PAS plugin.
        self.portal.acl_users.portal_role_manager.addRole('Producer')
        self.portal.acl_users.portal_role_manager.addRole('QA')
        self.portal.acl_users.portal_role_manager.addRole('Publisher')

        self.membership.addMember('producer', 'secret', ['Producer', 'Member',], [])
        self.membership.addMember('member', 'secret', ['Member',], [])
        self.membership.addMember('qa', 'secret', ['QA', 'Member',], [])
        self.membership.addMember('publisher', 'secret', ['Publisher','Member',], [])

        self.loginAsPortalOwner()
        self.portal.invokeFactory('Division', 'division')
        self.portal.division.invokeFactory('Course', 'course')
        self.portal.division.course.invokeFactory('Document', 'document')
        self.division = self.portal.division
        self.course = self.division.course
        self.logout()

    def beforeTearDown(self):
        self.loginAsPortalOwner()
        self.portal.manage_delObjects([self.division.id])
        self.logout()



    def testViewInProgressDocument(self):
        doc = self.division.course.document
        self.loginAsPortalOwner()

        # Owner is allowed
        self.failUnless(checkPerm(View, doc))
        # Member is not allowed
        self.login('member')
        self.failIf(checkPerm(View, doc))
        # Producer is allowed
        self.login('producer')
        self.failUnless(checkPerm(View, doc))
        # QA is allowed
        self.login('qa')
        self.failUnless(checkPerm(View, doc))
        # Publisher is allowed
        self.login('publisher')
        self.failUnless(checkPerm(View, doc))
        # Anonymous is not allowed
        self.logout()
        self.failIf(checkPerm(View, doc))

    def testViewQADocument(self):

        doc = self.division.course.document
        self.loginAsPortalOwner()
        self.portal.portal_workflow.doActionFor(doc, 'submit')

        # Owner is allowed
        self.failUnless(checkPerm(View, doc))
        # Member is not allowed
        self.login('member')
        self.failIf(checkPerm(View, doc))
        # Producer is allowed
        self.login('producer')
        self.failUnless(checkPerm(View, doc))
        # QA is allowed
        self.login('qa')
        self.failUnless(checkPerm(View, doc))
        # Publisher is allowed
        self.login('publisher')
        self.failUnless(checkPerm(View, doc))
        # Anonymous is not allowed
        self.logout()
        self.failIf(checkPerm(View, doc))

    def testViewReleasedDocument(self):

        doc = self.division.course.document
        self.loginAsPortalOwner()
        self.portal.portal_workflow.doActionFor(doc, 'submit')
        self.portal.portal_workflow.doActionFor(doc, 'release')

        # Owner is allowed
        self.failUnless(checkPerm(View, doc))
        # Member is not allowed
        self.login('member')
        self.failIf(checkPerm(View, doc))
        # Producer is allowed
        self.login('producer')
        self.failUnless(checkPerm(View, doc))
        # QA is allowed
        self.login('qa')
        self.failUnless(checkPerm(View, doc))
        # Publisher is allowed
        self.login('publisher')
        self.failUnless(checkPerm(View, doc))
        # Anonymous is not allowed
        self.logout()
        self.failIf(checkPerm(View, doc))

    def testViewPublishedDocument(self):

        doc = self.division.course.document
        self.loginAsPortalOwner()
        self.portal.portal_workflow.doActionFor(doc, 'submit')
        self.portal.portal_workflow.doActionFor(doc, 'release')
        self.portal.portal_workflow.doActionFor(doc, 'publish')

        # Owner is allowed
        self.failUnless(checkPerm(View, doc))
        # Member is allowed
        self.login('member')
        self.failUnless(checkPerm(View, doc))
        # Producer is allowed
        self.login('producer')
        self.failUnless(checkPerm(View, doc))
        # QA is allowed
        self.login('qa')
        self.failUnless(checkPerm(View, doc))
        # Publisher is allowed
        self.login('publisher')
        self.failUnless(checkPerm(View, doc))
        # Anonymous is allowed
        self.logout()
        self.failUnless(checkPerm(View, doc))

    def testAcessContentsInformationInProgressCourse(self):

        course = self.division.course
        self.loginAsPortalOwner()

        # Owner is allowed
        self.failUnless(checkPerm(AccessContentsInformation, course))
        # Member is not allowed
        self.login('member')
        self.failIf(checkPerm(AccessContentsInformation, course))
        # Producer is allowed
        self.login('producer')
        self.failUnless(checkPerm(AccessContentsInformation, course))
        # QA is allowed
        self.login('qa')
        self.failUnless(checkPerm(AccessContentsInformation, course))
        # Publisher is allowed
        self.login('publisher')
        self.failUnless(checkPerm(AccessContentsInformation, course))
        # Anonymous is not allowed
        self.logout()
        self.failIf(checkPerm(AccessContentsInformation, course))

    def testAccessContentsInformationQACourse(self):

        course = self.division.course
        self.loginAsPortalOwner()
        self.portal.portal_workflow.doActionFor(course, 'submit')

        # Owner is allowed
        self.failUnless(checkPerm(AccessContentsInformation, course))
        # Member is not allowed
        self.login('member')
        self.failIf(checkPerm(AccessContentsInformation, course))
        # Producer is allowed
        self.login('producer')
        self.failUnless(checkPerm(AccessContentsInformation, course))
        # QA is allowed
        self.login('qa')
        self.failUnless(checkPerm(AccessContentsInformation, course))
        # Publisher is allowed
        self.login('publisher')
        self.failUnless(checkPerm(AccessContentsInformation, course))
        # Anonymous is not allowed
        self.logout()
        self.failIf(checkPerm(AccessContentsInformation, course))

    def testAccessContentsInformationReleasedCourse(self):

        course = self.division.course
        self.loginAsPortalOwner()
        self.portal.portal_workflow.doActionFor(course, 'submit')
        self.portal.portal_workflow.doActionFor(course, 'release')

        # Owner is allowed
        self.failUnless(checkPerm(AccessContentsInformation, course))
        # Member is not allowed
        self.login('member')
        self.failIf(checkPerm(AccessContentsInformation, course))
        # Producer is allowed
        self.login('producer')
        self.failUnless(checkPerm(AccessContentsInformation, course))
        # QA is allowed
        self.login('qa')
        self.failUnless(checkPerm(AccessContentsInformation, course))
        # Publisher is allowed
        self.login('publisher')
        self.failUnless(checkPerm(AccessContentsInformation, course))
        # Anonymous is not allowed
        self.logout()
        self.failIf(checkPerm(AccessContentsInformation, course))

    def testAccessContentsInformationPublishedCourse(self):

        course = self.division.course
        self.loginAsPortalOwner()
        self.portal.portal_workflow.doActionFor(course, 'submit')
        self.portal.portal_workflow.doActionFor(course, 'release')
        self.portal.portal_workflow.doActionFor(course, 'publish')

        # Owner is allowed
        self.failUnless(checkPerm(AccessContentsInformation, course))
        # Member is allowed
        self.login('member')
        self.failUnless(checkPerm(AccessContentsInformation, course))
        # Producer is allowed
        self.login('producer')
        self.failUnless(checkPerm(AccessContentsInformation, course))
        # QA is allowed
        self.login('qa')
        self.failUnless(checkPerm(AccessContentsInformation, course))
        # Publisher is allowed
        self.login('publisher')
        self.failUnless(checkPerm(AccessContentsInformation, course))
        # Anonymous is allowed
        self.logout()
        self.failUnless(checkPerm(AccessContentsInformation, course))


    def testModifyPortalContentInProgressDocument(self):

        doc = self.division.course.document
        self.loginAsPortalOwner()

        # Owner is allowed
        self.failUnless(checkPerm(ModifyPortalContent, doc))
        # Member is not allowed
        self.login('member')
        self.failIf(checkPerm(ModifyPortalContent, doc))
        # Producer is allowed
        self.login('producer')
        self.failUnless(checkPerm(ModifyPortalContent, doc))
        # QA is not allowed
        self.login('qa')
        self.failIf(checkPerm(ModifyPortalContent, doc))
        # Publisher is not allowed
        self.login('publisher')
        self.failIf(checkPerm(ModifyPortalContent, doc))
        # Anonymous is not allowed
        self.logout()
        self.failIf(checkPerm(ModifyPortalContent, doc))

    def testModifyPortalContentQADocument(self):

        doc = self.division.course.document
        self.loginAsPortalOwner()
        self.portal.portal_workflow.doActionFor(doc, 'submit')
        # Owner is allowed
        self.failUnless(checkPerm(ModifyPortalContent, doc))
        # Member is not allowed
        self.login('member')
        self.failIf(checkPerm(ModifyPortalContent, doc))
        # Producer is not allowed
        self.login('producer')
        self.failIf(checkPerm(ModifyPortalContent, doc))
        # QA is not allowed
        self.login('qa')
        self.failIf(checkPerm(ModifyPortalContent, doc))
        # Publisher is not allowed
        self.login('publisher')
        self.failIf(checkPerm(ModifyPortalContent, doc))
        # Anonymous is not allowed
        self.logout()
        self.failIf(checkPerm(ModifyPortalContent, doc))

    def testModifyPortalContentReleasedDocument(self):

        doc = self.division.course.document
        self.loginAsPortalOwner()
        self.portal.portal_workflow.doActionFor(doc, 'submit')
        self.portal.portal_workflow.doActionFor(doc, 'release')

        # Owner is allowed
        self.failUnless(checkPerm(ModifyPortalContent, doc))

        # Member is not allowed
        self.login('member')
        self.failIf(checkPerm(ModifyPortalContent, doc))
        # Producer is not allowed
        self.login('producer')
        self.failIf(checkPerm(ModifyPortalContent, doc))
        # QA is not allowed
        self.login('qa')
        self.failIf(checkPerm(ModifyPortalContent, doc))
        # Publisher is not allowed
        self.login('publisher')
        self.failIf(checkPerm(ModifyPortalContent, doc))
        # Anonymous is not allowed
        self.logout()
        self.failIf(checkPerm(ModifyPortalContent, doc))

    def testModifyPortalContentPublishedDocument(self):

        doc = self.division.course.document
        self.loginAsPortalOwner()
        self.portal.portal_workflow.doActionFor(doc, 'submit')
        self.portal.portal_workflow.doActionFor(doc, 'release')
        self.portal.portal_workflow.doActionFor(doc, 'publish')

        # Owner is allowed
        self.failUnless(checkPerm(ModifyPortalContent, doc))
        # Member is not allowed
        self.login('member')
        self.failIf(checkPerm(ModifyPortalContent, doc))
        # Producer is not allowed
        self.login('producer')
        self.failIf(checkPerm(ModifyPortalContent, doc))
        # QA is not allowed
        self.login('qa')
        self.failIf(checkPerm(ModifyPortalContent, doc))
        # Publisher is not allowed
        self.login('publisher')
        self.failIf(checkPerm(ModifyPortalContent, doc))
        # Anonymous is not allowed
        self.logout()
        self.failIf(checkPerm(ModifyPortalContent, doc))

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestEditing))
    return suite

