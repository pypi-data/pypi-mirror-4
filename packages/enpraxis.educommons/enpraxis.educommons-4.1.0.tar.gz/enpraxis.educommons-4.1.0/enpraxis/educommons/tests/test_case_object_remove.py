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

import os, sys
from unittest import TestSuite, makeSuite
from Testing.ZopeTestCase import user_name
from AccessControl import Unauthorized
from Acquisition import aq_base
from base import eduCommonsTestCase

class testObjectRemove(eduCommonsTestCase):

    def afterSetUp(self):
        self.catalog = self.portal.portal_catalog
        self.workflow = self.portal.portal_workflow

        self.setRoles('Producer')
        self.portal.invokeFactory('Division', 'testDepartment')
        self.portal.testDepartment.invokeFactory('Course', 'testCourse')
        self.portal.testDepartment.testCourse.invokeFactory('Document', 'testDocument')
        self.portal.testDepartment.testCourse.invokeFactory('File', 'testFile')
        self.portal.testDepartment.testCourse.invokeFactory('Image', 'testImage')

        self.department = self.portal.testDepartment
        self.course = self.portal.testDepartment.testCourse
        self.document = self.portal.testDepartment.testCourse.testDocument
        self.file = self.portal.testDepartment.testCourse.testFile
        self.image = self.portal.testDepartment.testCourse.testImage

    def testRemoveObjectsAsAnonymous(self):
        self.logout()
        role = 'Anonymous'
        try:
            self.failIf(self.RemoveTestObject(role,obj=self.document))
        except Unauthorized,e:
            """We want this to fail"""
        try:
            self.failIf(self.RemoveTestObject(role,obj=self.image))
        except Unauthorized,e:
            """We want this to fail"""
        try:
            self.failIf(self.RemoveTestObject(role,obj=self.file))
        except Unauthorized,e:
            """We want this to fail"""
        try:
            self.failIf(self.RemoveTestObject(role,obj=self.course))
        except Unauthorized,e:
            """We want this to fail"""
        try:
            self.failIf(self.RemoveTestObject(role,obj=self.department))
        except Unauthorized,e:
            """We want this to fail"""

    def testRemoveObjectsAsOwner(self):
        self.setRoles('Owner')
        role = 'Owner'
        try:
            self.failIf(self.RemoveTestObject(role,obj=self.document))
        except Unauthorized,e:
            """We want this to fail"""
        try:
            self.failIf(self.RemoveTestObject(role,obj=self.image))
        except Unauthorized,e:
            """We want this to fail"""
        try:
            self.failIf(self.RemoveTestObject(role,obj=self.file))
        except Unauthorized,e:
            """We want this to fail"""
        try:
            self.failIf(self.RemoveTestObject(role,obj=self.course))
        except Unauthorized,e:
            """We want this to fail"""
        try:
            self.failIf(self.RemoveTestObject(role,obj=self.department))
        except Unauthorized,e:
            """We want this to fail"""

    def testRemoveObjectsAsPublisher(self):
        self.setRoles('Publisher') 
        role = 'Publisher'
        try:
            self.failIf(self.RemoveTestObject(role,obj=self.document))
        except Unauthorized,e:
            """We want this to fail"""
        try:
            self.failIf(self.RemoveTestObject(role,obj=self.image))
        except Unauthorized,e:
            """We want this to fail"""
        try:
            self.failIf(self.RemoveTestObject(role,obj=self.file))
        except Unauthorized,e:
            """We want this to fail"""
        try:
            self.failIf(self.RemoveTestObject(role,obj=self.course))
        except Unauthorized,e:
            """We want this to fail"""
        try:
            self.failIf(self.RemoveTestObject(role,obj=self.department))
        except Unauthorized,e:
            """We want this to fail"""
 
    def testRemoveObjectsAsProducer_InProgress(self):
        self.setRoles('Producer')
        #send in string, as setRoles doesn't get acquired in Remove methods
        role = 'Producer'
        self.failUnless(self.RemoveTestObject(role,obj=self.document))
        self.failUnless(self.RemoveTestObject(role,obj=self.image))
        self.failUnless(self.RemoveTestObject(role,obj=self.file))
        self.failUnless(self.RemoveTestObject(role,obj=self.course))
        self.failUnless(self.RemoveTestObject(role,obj=self.department))    


    def testRemoveObjectsAsProducer_QA_Released_Published(self):
        #A producer should not be allowed to delete an object in the released or published states
        #put the testDocument in the Released state and try to remove it
        self.setRoles('Producer')
        role = 'Producer'
        self.workflow.doActionFor(self.document,'submit')
        self.assertEqual(self.workflow.getInfoFor(self.document,'review_state'),'QA')   
        try:
            self.failIf(self.RemoveTestObject(role,obj=self.document))
        except Unauthorized,e:
            """We want this to fail"""

        self.setRoles('QA')
        self.workflow.doActionFor(self.document,'release')
        self.assertEqual(self.workflow.getInfoFor(self.document,'review_state'),'Released')   
        
        self.setRoles('Producer')
        try:
            self.failIf(self.RemoveTestObject(role,obj=self.document))
        except Unauthorized,e:
            """We want this to fail"""

        #put the testDocument in the Published state and try to remove it
        self.setRoles('Administrator')
        self.workflow.doActionFor(self.document,'publish')
        self.assertEqual(self.workflow.getInfoFor(self.document,'review_state'),'Published')   
        
        self.setRoles('Producer')
        try:
            self.failIf(self.RemoveTestObject(role,obj=self.document))
        except Unauthorized,e:
            """We want this to fail"""
            
    
    def testRemoveObjectsAsAdministrator(self):
        self.setRoles('Administrator')
        role = 'Administrator'
        self.failUnless(self.RemoveTestObject(role,obj=self.document))
        self.failUnless(self.RemoveTestObject(role,obj=self.image))
        self.failUnless(self.RemoveTestObject(role,obj=self.file))
        self.failUnless(self.RemoveTestObject(role,obj=self.course))
        self.failUnless(self.RemoveTestObject(role,obj=self.department))
 
    def testRemoveObjectsAsManager(self):
        self.setRoles('Manager')
        role = 'Manager'
        self.failUnless(self.RemoveTestObject(role,obj=self.document))
        self.failUnless(self.RemoveTestObject(role,obj=self.image))
        self.failUnless(self.RemoveTestObject(role,obj=self.file))
        self.failUnless(self.RemoveTestObject(role,obj=self.course))
        self.failUnless(self.RemoveTestObject(role,obj=self.department))
    
    def testRemoveObjectsAsViewer(self):
        self.setRoles('Viewer')
        role = 'Viewer'
        try:
            self.failIf(self.RemoveTestObject(role,obj=self.document))
        except Unauthorized,e:
            """We want this to fail"""
        try:
            self.failIf(self.RemoveTestObject(role,obj=self.image))
        except Unauthorized,e:
            """We want this to fail"""
        try:
            self.failIf(self.RemoveTestObject(role,obj=self.file))
        except Unauthorized,e:
            """We want this to fail"""
        try:
            self.failIf(self.RemoveTestObject(role,obj=self.course))
        except Unauthorized,e:
            """We want this to fail"""
        try:
            self.failIf(self.RemoveTestObject(role,obj=self.department))
        except Unauthorized,e:
            """We want this to fail"""
    
    def testRemoveObjectsAsQA(self):
        self.setRoles('QA')
        role = 'QA'
        try:
            self.failIf(self.RemoveTestObject(role,obj=self.document))
        except Unauthorized,e:
            """We want this to fail"""
        try:
            self.failIf(self.RemoveTestObject(role,obj=self.image))
        except Unauthorized,e:
            """We want this to fail"""
        try:
            self.failIf(self.RemoveTestObject(role,obj=self.file))
        except Unauthorized,e:
            """We want this to fail"""
        try:
            self.failIf(self.RemoveTestObject(role,obj=self.course))
        except Unauthorized,e:
            """We want this to fail"""
        try:
            self.failIf(self.RemoveTestObject(role,obj=self.department))
        except Unauthorized,e:
            """We want this to fail"""
    
    def testRemoveObjectsAsMember(self):
        self.setRoles('Member')
        role = 'Member'
        try:
            self.failIf(self.RemoveTestObject(role,obj=self.document))
        except Unauthorized,e:
            """We want this to fail"""
        try:
            self.failIf(self.RemoveTestObject(role,obj=self.image))
        except Unauthorized,e:
            """We want this to fail"""
        try:
            self.failIf(self.RemoveTestObject(role,obj=self.file))
        except Unauthorized,e:
            """We want this to fail"""
        try:
            self.failIf(self.RemoveTestObject(role,obj=self.course))
        except Unauthorized,e:
            """We want this to fail"""
        try:
            self.failIf(self.RemoveTestObject(role,obj=self.department))
        except Unauthorized,e:
            """We want this to fail"""
    

    def RemoveTestObject(self,role,obj=None):
        self.setRoles(role)
        obj_path = '/'.join(obj.getPhysicalPath())
        self.app.REQUEST.set('paths', [obj_path])
        parentFolder = obj.aq_parent
        parentFolder.manage_delObjects(obj.id)
        if hasattr(parentFolder,obj.id):
            return 0
        else:
            return 1    



def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(testObjectRemove))
    return suite

