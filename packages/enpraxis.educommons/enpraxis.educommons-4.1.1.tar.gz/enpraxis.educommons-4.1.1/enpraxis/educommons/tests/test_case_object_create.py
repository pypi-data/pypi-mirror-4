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

from AccessControl import Unauthorized
from Acquisition import aq_base
from base import eduCommonsTestCase
from base import eduCommonsTestCase

class testObjectCreate(eduCommonsTestCase):

    def afterSetUp(self):
        self.catalog = self.portal.portal_catalog
        self.workflow = self.portal.portal_workflow
                    
    def testCreateObjectsAsProducer(self):
	self.setRoles('Producer')
        department =  self.AddDepartment()
        course = self.AddCourse(dept=department.id)    
        self.AddDocument(context=course)
        self.AddImage(context=course)
        self.AddFile(context=course)
    
    def testCreateObjectsAsAdmin(self):
	self.setRoles('Administrator')
        department =  self.AddDepartment()
        course = self.AddCourse(dept=department.id)    
        self.AddDocument(context=course)
        self.AddImage(context=course)
        self.AddFile(context=course)
    
    def testCreateObjectsAsManager(self):
        self.setRoles('Manager')
        department =  self.AddDepartment()
        course = self.AddCourse(dept=department.id)    
        self.AddDocument(context=course)
        self.AddImage(context=course)
        self.AddFile(context=course)
    
    def testCreateObjectsAsQA(self):
	self.setRoles('QA')
        try:
            department =  self.AddDepartment()
            course = self.AddCourse(dept=department.id)    
            self.AddDocument(context=course)
            self.AddImage(context=course)
            self.AddFile(context=course)
            raise 'A qa user should not be allowed to create objects.'  
        except Unauthorized,e:
            """We want this to fail"""
    
    def testCreateObjectsAsMember(self):
	self.setRoles('Member')
        try:
            department =  self.AddDepartment()
            course = self.AddCourse(dept=department)    
            self.AddDocument(context=course)
            self.AddImage(context=course)
            self.AddFile(context=course)
            raise 'A member should not be allowed to create objects.'   
        except Unauthorized,e:
            """We want this to fail"""
    
    def testCreateObjectsAsAnonymous(self):
        try:
            department =  self.AddDepartment()
            course = self.AddCourse(dept=department)    
            self.AddDocument(context=course)
            self.AddImage(context=course)
            self.AddFile(context=course)
            raise 'An anonymous user should not be allowed to create objects.'  
        except Unauthorized,e:
            """We want this to fail"""

    def AddDocument(self,id='document',context=None):
        self.failIf(self.catalog(id=id))
        context.invokeFactory('Document', id)
        context.portal_factory.doCreate(context,id)
        self.failUnless(hasattr(aq_base(context), id))
        self.failUnless(self.catalog(id=id))

    def AddImage(self, id='image',context=None):
        self.failIf(self.catalog(id=id))
        context.invokeFactory('Image', id)
        self.failUnless(hasattr(aq_base(context), id))
        self.failUnless(self.catalog(id=id))

    def AddFile(self,id='file',context=None):
        self.failIf(self.catalog(id=id))
        context.invokeFactory('File', id)
        self.failUnless(hasattr(aq_base(context), id))
        self.failUnless(self.catalog(id=id))

    def AddDepartment(self,id='test-dept',context=None):
        self.failIf(self.catalog(id=id))
        context = self.portal
        context.invokeFactory('Division', id)
        self.failUnless(hasattr(aq_base(context), id))
        self.failUnless(self.catalog(id=id))
        return getattr(context,id)

    def AddCourse(self,id='test-course', dept='test-dept',context=None):
        self.failIf(self.catalog(id=id))
        self.failUnless(hasattr(self.portal,dept))
        context = getattr(self.portal,dept)
        context.invokeFactory('Course', id)
        self.failUnless(hasattr(aq_base(context), id))
        self.failUnless(self.catalog(id=id))
        return getattr(context,id)

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(testObjectCreate))
    return suite

