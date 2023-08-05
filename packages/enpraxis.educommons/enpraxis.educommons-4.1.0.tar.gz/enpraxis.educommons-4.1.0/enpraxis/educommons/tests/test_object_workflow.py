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

from Products.CMFCore.WorkflowCore import WorkflowException

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

class TestObjectWorkflow(eduCommonsTestCase):
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
        self.membership.addMember('manager', 'secret', ['Manager','Member',], [])

        self.loginAsPortalOwner()
        self.portal.invokeFactory('Division', 'division')
        self.portal.division.invokeFactory('Course', 'course')
        self.portal.division.course.invokeFactory('Document', 'document')
        self.division = self.portal.division
        self.course = self.division.course
        self.doc = self.division.course.document
        self.logout()

    def beforeTearDown(self):
        self.loginAsPortalOwner()
        self.portal.manage_delObjects([self.division.id])
        self.logout()

    def testManagerQADocument(self):
        self.login('manager')
        self.assertEqual(self.workflow.getInfoFor(self.doc, 'review_state'), 'InProgress')
        self.workflow.doActionFor(self.doc, 'submit')
        self.assertEqual(self.workflow.getInfoFor(self.doc, 'review_state'), 'QA')
        self.failUnless(self.catalog(id='document', review_state='QA'))

    def testManagerQAToInprogressDocument(self):
        self.login('manager')
        self.workflow.doActionFor(self.doc, 'submit')
        self.workflow.doActionFor(self.doc, 'reviewer_rework')
        self.assertEqual(self.workflow.getInfoFor(self.doc, 'review_state'), 'InProgress')
        self.failUnless(self.catalog(id='document', review_state='InProgress'))

    def testManagerQAToReleasedDocument(self):
        self.login('manager')
        self.workflow.doActionFor(self.doc, 'submit')
        self.workflow.doActionFor(self.doc, 'release')
        self.assertEqual(self.workflow.getInfoFor(self.doc, 'review_state'), 'Released')
        self.failUnless(self.catalog(id='document', review_state='Released'))

    def testManagerReleaseToPublished(self):
        self.login('manager')
        self.workflow.doActionFor(self.doc, 'submit')
        self.workflow.doActionFor(self.doc, 'release')
        self.workflow.doActionFor(self.doc, 'publish')
        self.assertEqual(self.workflow.getInfoFor(self.doc, 'review_state'), 'Published')
        self.failUnless(self.catalog(id='document', review_state='Published'))

    def testManagerReleaseToQA(self):
        self.login('manager')
        self.workflow.doActionFor(self.doc, 'submit')
        self.workflow.doActionFor(self.doc, 'release')
        self.assertEqual(self.workflow.getInfoFor(self.doc, 'review_state'), 'Released')
        self.workflow.doActionFor(self.doc, 'publisher_retest')
        self.assertEqual(self.workflow.getInfoFor(self.doc, 'review_state'), 'QA')
        self.failUnless(self.catalog(id='document', review_state='QA'))

    def testManagerReleasedToInProgress(self):
        self.login('manager')
        self.workflow.doActionFor(self.doc, 'submit')
        self.workflow.doActionFor(self.doc, 'release')
        self.assertEqual(self.workflow.getInfoFor(self.doc, 'review_state'), 'Released')
        self.workflow.doActionFor(self.doc, 'publisher_rework')
        self.assertEqual(self.workflow.getInfoFor(self.doc, 'review_state'), 'InProgress')
        self.failUnless(self.catalog(id='document', review_state='InProgress'))

    def testManagerPublishedToInProgress(self):
        self.login('manager')
        self.workflow.doActionFor(self.doc, 'submit')
        self.workflow.doActionFor(self.doc, 'release')
        self.workflow.doActionFor(self.doc, 'publish')
        self.assertEqual(self.workflow.getInfoFor(self.doc, 'review_state'), 'Published')
        self.workflow.doActionFor(self.doc, 'manager_rework')
        self.assertEqual(self.workflow.getInfoFor(self.doc, 'review_state'), 'InProgress')
        self.failUnless(self.catalog(id='document', review_state='InProgress'))

    def testProducerSubmitsInProgressDocument(self):
        self.loginAsPortalOwner()
        self.assertEqual(self.workflow.getInfoFor(self.doc, 'review_state'), 'InProgress')
        self.login('producer')
        self.workflow.doActionFor(self.doc, 'submit')
        self.assertEqual(self.workflow.getInfoFor(self.doc, 'review_state'), 'QA')
        self.failUnless(self.catalog(id='document', review_state='QA'))

    def testQAReleasesQADocument(self):
        self.loginAsPortalOwner()
        self.workflow.doActionFor(self.doc, 'submit')
        self.assertEqual(self.workflow.getInfoFor(self.doc, 'review_state'), 'QA')
        self.login('qa')
        self.workflow.doActionFor(self.doc, 'release')
        self.assertEqual(self.workflow.getInfoFor(self.doc, 'review_state'), 'Released')
        self.failUnless(self.catalog(id='document', review_state='Released'))

    def testQAReworkQADocument(self):
        self.loginAsPortalOwner()
        self.workflow.doActionFor(self.doc, 'submit')
        self.assertEqual(self.workflow.getInfoFor(self.doc, 'review_state'), 'QA')
        self.login('qa')
        self.workflow.doActionFor(self.doc, 'reviewer_rework')
        self.assertEqual(self.workflow.getInfoFor(self.doc, 'review_state'), 'InProgress')
        self.failUnless(self.catalog(id='document', review_state='InProgress'))

    def testPublisherPublishesReleasedDocument(self):
        self.loginAsPortalOwner()
        self.workflow.doActionFor(self.doc, 'submit')
        self.workflow.doActionFor(self.doc, 'release')
        self.assertEqual(self.workflow.getInfoFor(self.doc, 'review_state'), 'Released')
        self.login('publisher')
        self.workflow.doActionFor(self.doc, 'publish')
        self.assertEqual(self.workflow.getInfoFor(self.doc, 'review_state'), 'Published')
        self.failUnless(self.catalog(id='document', review_state='Published'))

    def testPublisherReworksReleasedDocument(self):
        self.loginAsPortalOwner()
        self.workflow.doActionFor(self.doc, 'submit')
        self.workflow.doActionFor(self.doc, 'release')
        self.assertEqual(self.workflow.getInfoFor(self.doc, 'review_state'), 'Released')
        self.login('publisher')
        self.workflow.doActionFor(self.doc, 'publisher_rework')
        self.assertEqual(self.workflow.getInfoFor(self.doc, 'review_state'), 'InProgress')
        self.failUnless(self.catalog(id='document', review_state='InProgress'))

    def testPublisherRetestssReleasedDocument(self):
        self.loginAsPortalOwner()
        self.workflow.doActionFor(self.doc, 'submit')
        self.workflow.doActionFor(self.doc, 'release')
        self.assertEqual(self.workflow.getInfoFor(self.doc, 'review_state'), 'Released')
        self.login('publisher')
        self.workflow.doActionFor(self.doc, 'publisher_retest')
        self.assertEqual(self.workflow.getInfoFor(self.doc, 'review_state'), 'QA')
        self.failUnless(self.catalog(id='document', review_state='QA'))

    # Check some forbidden transitions

    def testQAPublishesDocument(self):
        self.loginAsPortalOwner()
        self.workflow.doActionFor(self.doc, 'submit')
        self.workflow.doActionFor(self.doc, 'release')
        self.assertEqual(self.workflow.getInfoFor(self.doc, 'review_state'), 'Released')
        self.login('qa')
        try:
            self.workflow.doActionFor(self.doc, 'publish')
        except WorkflowException:
            # This should fail with a WorkflowException
            pass

    def testPublisherQASDocument(self):
        self.loginAsPortalOwner()
        self.assertEqual(self.workflow.getInfoFor(self.doc, 'review_state'), 'InProgress')
        self.login('publisher')
        try:
            self.workflow.doActionFor(self.doc, 'submit')
        except WorkflowException:
            # This should fail with a WorkflowException
            pass


    def testProducerRetestsDocument(self):
        self.loginAsPortalOwner()
        self.workflow.doActionFor(self.doc, 'submit')
        self.workflow.doActionFor(self.doc, 'release')
        self.assertEqual(self.workflow.getInfoFor(self.doc, 'review_state'), 'Released')
        self.login('producer')
        try:
            self.workflow.doActionFor(self.doc, 'publisher_retest')
        except WorkflowException:
            # This should fail with a WorkflowException
            pass

    def testPublisherReworksDocument(self):
        self.loginAsPortalOwner()
        self.workflow.doActionFor(self.doc, 'submit')
        self.workflow.doActionFor(self.doc, 'release')
        self.workflow.doActionFor(self.doc, 'publish')
        self.assertEqual(self.workflow.getInfoFor(self.doc, 'review_state'), 'Published')
        self.login('publisher')
        try:
            self.workflow.doActionFor(self.doc, 'manager_rework')
        except WorkflowException:
            # This should fail with a WorkflowException
            pass
        

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestObjectWorkflow))
    return suite

