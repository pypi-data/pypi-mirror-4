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

class TestObjectEditing(eduCommonsTestCase):
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
        self.logout()

    def beforeTearDown(self):
        self.loginAsPortalOwner()
        self.portal.manage_delObjects([self.division.id])
        self.logout()

    def testManagerModifyInProgressDocument(self):

        doc = self.division.course.document
        self.login('manager')
        doc.edit(title = 'Document 1')
        self.assertEqual(doc.title, 'Document 1')

    def testProducerModifyInProgressDocument(self):

        doc = self.division.course.document
        self.loginAsPortalOwner()
        doc.edit(title = 'Document 1')
        self.login('producer')
        doc.edit(title = 'Document 2')
        self.assertEqual(doc.title, 'Document 2')

    def testQAModifyInProgressDocument(self):

        doc = self.division.course.document
        self.loginAsPortalOwner()
        doc.edit(title = 'Document 1')
        self.login('qa')
        doc.edit(title = 'Document 2')
        self.assertEqual(doc.title, 'Document 1')

    def testPublisherModifyInProgressDocument(self):

        doc = self.division.course.document
        self.loginAsPortalOwner()
        doc.edit(title = 'Document 1')
        self.login('publisher')
        doc.edit(title = 'Document 2')
        self.assertEqual(doc.title, 'Document 1')

    def testManagerModifyQADocument(self):

        doc = self.division.course.document
        self.login('manager')
        self.workflow.doActionFor(doc, 'submit')
        doc.edit(title = 'Document 1')
        self.assertEqual(doc.title, 'Document 1')

    def testProducerModifyQADocument(self):

        doc = self.division.course.document
        self.loginAsPortalOwner()
        self.workflow.doActionFor(doc, 'submit')
        doc.edit(title = 'Document 1')
        self.login('producer')
        doc.edit(title = 'Document 2')
        self.assertEqual(doc.title, 'Document 1')

    def testQAModifyQADocument(self):

        doc = self.division.course.document
        self.loginAsPortalOwner()
        self.workflow.doActionFor(doc, 'submit')
        doc.edit(title = 'Document 1')
        self.login('qa')
        doc.edit(title = 'Document 2')
        self.assertEqual(doc.title, 'Document 1')

    def testPublisherModifyQADocument(self):

        doc = self.division.course.document
        self.loginAsPortalOwner()
        self.workflow.doActionFor(doc, 'submit')
        doc.edit(title = 'Document 1')
        self.login('publisher')
        doc.edit(title = 'Document 2')
        self.assertEqual(doc.title, 'Document 1')


    def testManagerModifyReleasedDocument(self):

        doc = self.division.course.document
        self.login('manager')
        self.workflow.doActionFor(doc, 'submit')
        self.workflow.doActionFor(doc, 'release')
        doc.edit(title = 'Document 1')
        self.assertEqual(doc.title, 'Document 1')

    def testProducerModifyReleasedDocument(self):

        doc = self.division.course.document
        self.loginAsPortalOwner()
        self.workflow.doActionFor(doc, 'submit')
        self.workflow.doActionFor(doc, 'release')
        doc.edit(title = 'Document 1')
        self.login('producer')
        doc.edit(title = 'Document 2')
        self.assertEqual(doc.title, 'Document 1')

    def testQAModifyReleasedDocument(self):

        doc = self.division.course.document
        self.loginAsPortalOwner()
        self.workflow.doActionFor(doc, 'submit')
        self.workflow.doActionFor(doc, 'release')
        doc.edit(title = 'Document 1')
        self.login('qa')
        doc.edit(title = 'Document 2')
        self.assertEqual(doc.title, 'Document 1')

    def testPublisherModifyReleasedDocument(self):

        doc = self.division.course.document
        self.loginAsPortalOwner()
        self.workflow.doActionFor(doc, 'submit')
        self.workflow.doActionFor(doc, 'release')
        doc.edit(title = 'Document 1')
        self.login('publisher')
        doc.edit(title = 'Document 2')
        self.assertEqual(doc.title, 'Document 1')


    def testManagerModifyPublishedDocument(self):

        doc = self.division.course.document
        self.login('manager')
        self.workflow.doActionFor(doc, 'submit')
        self.workflow.doActionFor(doc, 'release')
        self.workflow.doActionFor(doc, 'publish')
        doc.edit(title = 'Document 1')
        self.assertEqual(doc.title, 'Document 1')

    def testProducerModifyPublishedDocument(self):

        doc = self.division.course.document
        self.loginAsPortalOwner()
        self.workflow.doActionFor(doc, 'submit')
        self.workflow.doActionFor(doc, 'release')
        self.workflow.doActionFor(doc, 'publish')
        doc.edit(title = 'Document 1')
        self.login('producer')
        doc.edit(title = 'Document 2')
        self.assertEqual(doc.title, 'Document 1')

    def testQAModifyPublishedDocument(self):

        doc = self.division.course.document
        self.loginAsPortalOwner()
        self.workflow.doActionFor(doc, 'submit')
        self.workflow.doActionFor(doc, 'release')
        self.workflow.doActionFor(doc, 'publish')
        doc.edit(title = 'Document 1')
        self.login('qa')
        doc.edit(title = 'Document 2')
        self.assertEqual(doc.title, 'Document 1')

    def testPublisherModifyPublishedDocument(self):

        doc = self.division.course.document
        self.loginAsPortalOwner()
        self.workflow.doActionFor(doc, 'submit')
        self.workflow.doActionFor(doc, 'release')
        self.workflow.doActionFor(doc, 'publish')
        doc.edit(title = 'Document 1')
        self.login('publisher')
        doc.edit(title = 'Document 2')
        self.assertEqual(doc.title, 'Document 1')

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestObjectEditing))
    return suite

