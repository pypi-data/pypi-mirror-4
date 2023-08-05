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

from unittest import TestSuite, makeSuite
from AccessControl import Unauthorized
from Acquisition import aq_base
from base import eduCommonsTestCase
from zope.annotation.interfaces import IAnnotations
import sys
from Testing.ZopeTestCase import user_name

class testObjectEdit(eduCommonsTestCase):

    def afterSetUp(self):
        self.catalog = self.portal.portal_catalog
        self.workflow = self.portal.portal_workflow

    def testEditing(self):  
        """Test for editing"""
        wftool = self.portal.portal_workflow
        self.setRoles('Producer')
        self.portal.invokeFactory('Division', 'testDepartment')
        self.portal.testDepartment.invokeFactory('Course', 'testCourse')
        self.portal.testDepartment.testCourse.invokeFactory('Document', 'testDocument')
        self.portal.testDepartment.testCourse.invokeFactory('File', 'testFile')
        self.portal.testDepartment.testCourse.invokeFactory('Image', 'testImage')
  
 
        self.testdepartment = self.portal.testDepartment
        self.testcourse = self.portal.testDepartment.testCourse
        self.testdoc = self.portal.testDepartment.testCourse.testDocument
        self.testfile = self.portal.testDepartment.testCourse.testFile
        self.testimage = self.portal.testDepartment.testCourse.testImage
   
        self.EditObjectsAsProducer()
        self.EditObjectsAsManager()
        self.EditObjectsAsQA()
        self.EditObjectsAsPublisher()
        self.EditObjectsAsMember()
        self.EditObjectsAsAnonymous()
       
        self.login(user_name)
        self.setRoles('Manager')       
 
        #move everything to qa
        wftool.doActionFor(self.testdepartment,'submit')
        wftool.doActionFor(self.testcourse,'submit')
        wftool.doActionFor(self.testdoc,'submit')
        wftool.doActionFor(self.testimage,'submit')
        wftool.doActionFor(self.testfile,'submit')
        
        self.assertEqual(self.workflow.getInfoFor(self.testdepartment, 'review_state'), 'QA')  
        self.assertEqual(self.workflow.getInfoFor(self.testcourse, 'review_state'), 'QA')  
        self.assertEqual(self.workflow.getInfoFor(self.testdoc, 'review_state'), 'QA')  
        self.assertEqual(self.workflow.getInfoFor(self.testfile, 'review_state'), 'QA')  
        self.assertEqual(self.workflow.getInfoFor(self.testimage, 'review_state'), 'QA')  
   
        self.EditObjectsAsProducer()
        self.EditObjectsAsManager()
        self.EditObjectsAsQA()
        self.EditObjectsAsPublisher()
        self.EditObjectsAsMember()
        self.EditObjectsAsAnonymous()
        
        self.login(user_name) 
        self.setRoles('Manager')       

        #move everything to released
        wftool.doActionFor(self.testdepartment,'release')
        wftool.doActionFor(self.testcourse,'release')
        wftool.doActionFor(self.testdoc,'release')
        wftool.doActionFor(self.testimage,'release')
        wftool.doActionFor(self.testfile,'release')

        self.assertEqual(self.workflow.getInfoFor(self.testdepartment, 'review_state'), 'Released')  
        self.assertEqual(self.workflow.getInfoFor(self.testcourse, 'review_state'), 'Released')  
        self.assertEqual(self.workflow.getInfoFor(self.testdoc, 'review_state'), 'Released')  
        self.assertEqual(self.workflow.getInfoFor(self.testfile, 'review_state'), 'Released')  
        self.assertEqual(self.workflow.getInfoFor(self.testimage, 'review_state'), 'Released')  
        
        self.EditObjectsAsProducer()
        self.EditObjectsAsManager()
        self.EditObjectsAsQA()
        self.EditObjectsAsPublisher()
        self.EditObjectsAsMember()
        self.EditObjectsAsAnonymous()
        
        self.login(user_name)
        self.setRoles('Manager')       
        
        #move everything to published
        wftool.doActionFor(self.testdepartment,'publish')
        wftool.doActionFor(self.testcourse,'publish')
        wftool.doActionFor(self.testdoc,'publish')
        wftool.doActionFor(self.testimage,'publish')
        wftool.doActionFor(self.testfile,'publish')
                
        self.assertEqual(self.workflow.getInfoFor(self.testdepartment, 'review_state'), 'Published')  
        self.assertEqual(self.workflow.getInfoFor(self.testcourse, 'review_state'), 'Published')  
        self.assertEqual(self.workflow.getInfoFor(self.testdoc, 'review_state'), 'Published')  
        self.assertEqual(self.workflow.getInfoFor(self.testfile, 'review_state'), 'Published')  
        self.assertEqual(self.workflow.getInfoFor(self.testimage, 'review_state'), 'Published')  
        
        self.EditObjectsAsProducer()
        self.EditObjectsAsManager()
        self.EditObjectsAsQA()
        self.EditObjectsAsPublisher()
        self.EditObjectsAsMember()
        self.EditObjectsAsAnonymous()
        
    def EditObjectsAsProducer(self):
        self.setRoles('Producer')
        try:
            if self.portal.portal_membership.checkPermission("Modify portal content", self.testcourse):
                self.testcourse.setTitle('test title')
                self.testcourse.setText('test Text')
                self.testcourse.setDescription('test Description')
                IAnnotations(self.testcourse)['eduCommons.clearcopyright'] = 1
            else:
                raise Unauthorized
        except:
            if sys.exc_type != 'Unauthorized' and sys.exc_type != Unauthorized:
                raise sys.exc_type
            else:
                """We want this to fail"""
                if self.workflow.getInfoFor(self.testcourse,'review_state') == 'InProgress':
                    raise 'A producer user should be allowed to edit courses.' 

        try:
            if self.portal.portal_membership.checkPermission("Modify portal content", self.testdepartment):
                self.testdepartment.setTitle('test title')
                self.testdepartment.setText('test Text')
                self.testdepartment.setDescription('test Description')
                IAnnotations(self.testdepartment)['educommons.clearcopyright'] = 1
            else:
                raise Unauthorized
        except:
            if not sys.exc_type == 'Unauthorized' and sys.exc_type != Unauthorized:
                raise sys.exc_type
            else:
                """We want this to fail"""
                if self.workflow.getInfoFor(self.testdepartment,'review_state') == 'InProgress':
                   raise 'A producer user should be allowed to edit departments.' 
               
        try:
            if self.portal.portal_membership.checkPermission("Modify portal content", self.testdoc):
                self.testdoc.setTitle('test title')
                self.testdoc.setText('test Text')
                self.testdoc.setDescription('test Description')
                IAnnotations(self.testdoc)['educommons.clearcopyright'] = 1
            else:
                raise Unauthorized
        except:
            if not sys.exc_type == 'Unauthorized' and sys.exc_type != Unauthorized:
                raise sys.exc_type
            else:
                """We want this to fail"""
                if self.workflow.getInfoFor(self.testdoc,'review_state') == 'InProgress':
                   raise 'A producer user should be allowed to edit ecdocuments.' 
               
        try:
            if self.portal.portal_membership.checkPermission("Modify portal content", self.testimage):
                self.testimage.setTitle('test Title')
                self.testimage.setExcludeFromNav(False)
                self.testimage.setDescription('test Image')
                self.testimage.setImage(None)
                IAnnotations(self.testimage)['educommons.clearcopyright'] = 1
            else:
                raise Unauthorized
        except:
            if not sys.exc_type == 'Unauthorized' and sys.exc_type != Unauthorized:
                raise sys.exc_type
            else:
                """We want this to fail"""
                if self.workflow.getInfoFor(self.testimage,'review_state') == 'InProgress':
                   raise 'A producer user should be allowed to edit vimages.' 
        
        try:
            if self.portal.portal_membership.checkPermission("Modify portal content", self.testfile):
                self.testfile.setTitle('test Title')
                self.testfile.setExcludeFromNav(False)
                self.testfile.setDescription('test Image')
                self.testfile.setFile(None)
                IAnnotations(self.testfile)['educommons.clearcopyright'] = 1            
            else:
                raise Unauthorized
        except:
            if not sys.exc_type == 'Unauthorized' and sys.exc_type != Unauthorized:
                raise sys.exc_type
            else:
                """We want this to fail"""
                if self.workflow.getInfoFor(self.testfile,'review_state') == 'InProgress':
                   raise 'A producer user should be allowed to edit files.' 


    def EditObjectsAsManager(self):
        self.setRoles('Manager')       
        try:
            if self.portal.portal_membership.checkPermission("Modify portal content", self.testcourse):
                self.testcourse.setTitle('test title')
                self.testcourse.setText('test Text')
                self.testcourse.setDescription('test Description')
                IAnnotations(self.testcourse)['educommons.clearcopyright'] = 1
            else:
                raise Unauthorized
        except Unauthorized,e:
            """We want this to fail"""
            raise 'A manager user should be allowed to edit courses.' 
        
        try:
            if self.portal.portal_membership.checkPermission("Modify portal content", self.testdepartment):
                self.testdepartment.setTitle('test title')
                self.testdepartment.setText('test Text')
                self.testdepartment.setDescription('test Description')
                IAnnotations(self.testdepartment)['educommons.clearcopyright'] = 1
            else:
                Unauthorized
        except Unauthorized,e:
            """We want this to fail"""
            raise 'A manager user should be allowed to edit departments.' 
           
        try:
            if self.portal.portal_membership.checkPermission("Modify portal content", self.testdoc):
                self.testdoc.setTitle('test title')
                self.testdoc.setText('test Text')
                self.testdoc.setDescription('test Description')
                IAnnotations(self.testdoc)['educommons.clearcopyright'] = 1
            else:
                raise Unauthorized
        except Unauthorized,e:
            """We want this to fail"""
            raise 'A manager user should be allowed to edit documents.' 
           
        try:
            if self.portal.portal_membership.checkPermission("Modify portal content", self.testimage):
                self.testimage.setTitle('test Title')
                self.testimage.setExcludeFromNav(False)
                self.testimage.setDescription('test Image')
                self.testimage.setImage(None)
                IAnnotations(self.testimage)['educommons.clearcopyright'] = 1
            else:
                raise Unauthorized
        except Unauthorized,e:
            """We want this to fail"""
            raise 'A manager user should be allowed to edit images.' 
        
        try:
            if self.portal.portal_membership.checkPermission("Modify portal content", self.testfile):
                self.testfile.setTitle('test Title')
                self.testfile.setExcludeFromNav(False)
                self.testfile.setDescription('test Image')
                self.testfile.setFile(None)
                IAnnotations(self.testfile)['educommons.clearcopyright'] = 1
            else:
                raise Unauthorized
        except Unauthorized,e:
            """We want this to fail"""
            raise 'A manager user should be allowed to edit files.' 

    def EditObjectsAsQA(self):
        self.setRoles('QA') 
        try:
            if self.portal.portal_membership.checkPermission("Modify portal content", self.testcourse):
                self.testcourse.setTitle('test title')
                self.testcourse.setText('test Text')
                self.testcourse.setDescription('test Description')
                IAnnotations(self.testcourse)['educommons.clearcopyright'] = 1
                raise 'A qa user should not be allowed to edit courses.' 
            else:
                raise Unauthorized 
        except Unauthorized,e:
            """We want this to fail"""
        
        try:
            if self.portal.portal_membership.checkPermission("Modify portal content", self.testdepartment):
                self.testdepartment.setTitle('test title')
                self.testdepartment.setText('test Text')
                self.testdepartment.setDescription('test Description')
                IAnnotations(self.testdepartment)['educommons.clearcopyright'] = 1
                raise 'A qa user should not be allowed to edit departments.' 
            else:
                raise Unauthorized 
        except Unauthorized,e:
            """We want this to fail"""
           
        try:
            if self.portal.portal_membership.checkPermission("Modify portal content", self.testdoc):
                self.testdoc.setTitle('test title')
                self.testdoc.setText('test Text')
                self.testdoc.setDescription('test Description')
                IAnnotations(self.testdoc)['educommons.clearcopyright'] = 1
                raise 'A qa user should not be allowed to edit documents.'
            else:
                raise Unauthorized
        except:
            """We want this to fail"""
            if not sys.exc_type == 'Unauthorized' and sys.exc_type != Unauthorized:
                raise sys.exc_type
           
        try:
            if self.portal.portal_membership.checkPermission("Modify portal content", self.testimage):
                self.testimage.setTitle('test Title')
                self.testimage.setExcludeFromNav(False)
                self.testimage.setDescription('test Image')
                self.testimage.setImage(None)
                IAnnotations(self.testimage)['educommons.clearcopyright'] = 1
                raise 'A qa user should not be allowed to edit images.'  
            else:
                raise Unauthorized
        except:
            """We want this to fail"""
            if not sys.exc_type == 'Unauthorized' and sys.exc_type != Unauthorized:
                raise sys.exc_type
        
        try:
            if self.portal.portal_membership.checkPermission("Modify portal content", self.testfile):
                self.testfile.setTitle('test Title')
                self.testfile.setExcludeFromNav(False)
                self.testfile.setDescription('test Image')
                self.testfile.setFile(None)
                IAnnotations(self.testfile)['educommons.clearcopyright'] = 1
                raise 'A qa user should not be allowed to edit files.'  
            else:
                raise Unauthorized
        except:
            """We want this to fail"""
            if not sys.exc_type == 'Unauthorized' and sys.exc_type != Unauthorized:
                raise sys.exc_type

    def EditObjectsAsPublisher(self):
        self.setRoles('Publisher') 
        try:
            if self.portal.portal_membership.checkPermission("Modify portal content", self.testcourse):
                self.testcourse.setTitle('test title')
                self.testcourse.setText('test Text')
                self.testcourse.setDescription('test Description')
                IAnnotations(self.testcourse)['educommons.clearcopyright'] = 1
                raise 'A publisher user should not be allowed to edit courses.'
            else:
                raise Unauthorized
        except Unauthorized,e:
            """We want this to fail"""
        
        try:
            if self.portal.portal_membership.checkPermission("Modify portal content", self.testdepartment):
                self.testdepartment.setTitle('test title')
                self.testdepartment.setText('test Text')
                self.testdepartment.setDescription('test Description')
                IAnnotations(self.testdepartment)['educommons.clearcopyright'] = 1
                raise 'A publisher user should not be allowed to edit departments.'  
            else:
                raise Unauthorized
        except Unauthorized,e:
            """We want this to fail"""
           
        try:
            if self.portal.portal_membership.checkPermission("Modify portal content", self.testdoc):
                self.testdoc.setTitle('test title')
                self.testdoc.setText('test Text')
                self.testdoc.setDescription('test Description')
                IAnnotations(self.testdoc)['educommons.clearcopyright'] = 1
                raise 'A publisher user should not be allowed to edit documents.' 
            else:
                raise Unauthorized
        except:
            """We want this to fail"""
            if not sys.exc_type == 'Unauthorized' and sys.exc_type != Unauthorized:
                raise sys.exc_type
           
        try:
            if self.portal.portal_membership.checkPermission("Modify portal content", self.testimage):
                self.testimage.setTitle('test Title')
                self.testimage.setExcludeFronNav(0)
                self.testimage.setDescription('test Image')
                self.testimage.setImage(None)
                IAnnotations(self.testimage)['educommons.clearcopyright'] = 1
                raise 'A publisher user should not be allowed to edit images.'  
            else:
                raise Unauthorized
        except:
            """We want this to fail"""
            if not sys.exc_type == 'Unauthorized' and sys.exc_type != Unauthorized:
                raise sys.exc_type
        
        try:
            if self.portal.portal_membership.checkPermission("Modify portal content", self.testfile):
                self.testfile.setTitle('test Title')
                self.testfile.setExcludeFromNav(False)
                self.testfile.setDescription('test Image')
                self.testfile.setFile(None)
                IAnnotations(self.testfile)['educommons.clearcopyright'] = 1
                raise 'A publisher user should not be allowed to edit files.'
            else:
                raise Unauthorized
        except:
            """We want this to fail"""
            if not sys.exc_type == 'Unauthorized' and sys.exc_type != Unauthorized:
                raise sys.exc_type

    def EditObjectsAsMember(self):
        self.setRoles('Member') 
        
        try:
            if self.portal.portal_membership.checkPermission("Modify portal content", self.testcourse):
                self.testcourse.setTitle('test title')
                self.testcourse.setText('test Text')
                self.testcourse.setDescription('test Description')
                IAnnotations(self.testcourse)['educommons.clearcopyright'] = 1
                raise 'A member user should not be allowed to edit courses.'  
            else:
                raise Unauthorized
        except:
            """We want this to fail"""
            if not sys.exc_type == 'Unauthorized' and sys.exc_type != Unauthorized:
                raise sys.exc_type
        
        try:
            if self.portal.portal_membership.checkPermission("Modify portal content", self.testdepartment):
                self.testdepartment.setTitle('test title')
                self.testdepartment.setText('test Text')
                self.testdepartment.setDescription('test Description')
                IAnnotations(self.testdepartment)['educommons.clearcopyright'] = 1
                raise 'A member user should not be allowed to edit departments.'  
            else:
                raise Unauthorized
        except:
            """We want this to fail"""
            if not sys.exc_type == 'Unauthorized' and sys.exc_type != Unauthorized:
                raise sys.exc_type
           
        try:
            if self.portal.portal_membership.checkPermission("Modify portal content", self.testdoc):
                self.testdoc.setTitle('test title')
                self.testdoc.setText('test Text')
                self.testdoc.setDescription('test Description')
                IAnnotations(self.testdoc)['educommons.clearcopyright'] = 1
                raise 'A member user should not be allowed to edit documents.'
            else:
                raise Unauthorized
        except:
            """We want this to fail"""
            if not sys.exc_type == 'Unauthorized' and sys.exc_type != Unauthorized:
                raise sys.exc_type
           
        try:
            if self.portal.portal_membership.checkPermission("Modify portal content", self.testimage):
                self.testimage.setTitle('test Title')
                self.testimage.setExcludeFromNav(False)
                self.testimage.setDescription('test Image')
                self.testimage.setImage(None)
                IAnnotations(self.testimage)['educommons.clearcopyright'] = 1
                raise 'A member user should not be allowed to edit images.'
            else:
                raise Unauthorized
        except:
            """We want this to fail"""
            if not sys.exc_type == 'Unauthorized' and sys.exc_type != Unauthorized:
                raise sys.exc_type
        
        try:
            if self.portal.portal_membership.checkPermission("Modify portal content", self.testfile):
                self.testfile.setTitle('test Title')
                self.testfile.setExcludeFromNav(False)
                self.testfile.setDescription('test Image')
                self.testfile.setFile(None)
                IAnnotations(self.testfile)['educommons.clearcopyright'] = 1
                raise 'A member user should not be allowed to edit files.'
            else:
                raise Unauthorized
        except:
            """We want this to fail"""
            if not sys.exc_type == 'Unauthorized' and sys.exc_type != Unauthorized:
                raise sys.exc_type

    def EditObjectsAsAnonymous(self):
        self.logout() 
        try:
            if str(self.portal.portal_membership.getAuthenticatedMember())=='Anonymous User':
                raise Unauthorized
            else:
                self.testcourse.setTitle('test title')
                self.testcourse.setText('test Text')
                self.testcourse.setDescription('test Description')
                IAnnotations(self.testcourse)['educommons.clearcopyright'] = 1
                raise 'An anonymous user should not be allowed to edit courses.'  
        except Unauthorized,e:
            """We want this to fail"""
        
        try:
            if str(self.portal.portal_membership.getAuthenticatedMember())=='Anonymous User':
                raise Unauthorized
            else:
                self.testdepartment.setTitle('test title')
                self.testdepartment.setText('test Text')
                self.testdepartment.setDescription('test Description')
                IAnnotations(self.testdepartment)['educommons.clearcopyright'] = 1
                raise 'An anonymous user should not be allowed to edit departments.'  
        except Unauthorized,e:
            """We want this to fail"""
           
        try:
            if str(self.portal.portal_membership.getAuthenticatedMember())=='Anonymous User':
                raise Unauthorized
            else:
                self.testdoc.setTitle('test title')
                self.testdoc.setText('test Text')
                self.testdoc.setDescription('test Description')
                IAnnotations(self.testdoc)['educommons.clearcopyright'] = 1
                raise 'An anonymous user should not be allowed to edit documents.'
        except Unauthorized,e:
            """We want this to fail"""
           
        try:
            if str(self.portal.portal_membership.getAuthenticatedMember())=='Anonymous User':
                raise Unauthorized
            else:
                self.testimage.setTitle('test Title')
                self.testimage.setExcludeFromNav(False)
                self.testimage.setDescription('test Image')
                self.testimage.setImage(None)
                IAnnotations(self.testimage)['educommons.clearcopyright'] = 1
                raise 'An anonymous user should not be allowed to edit images.'
        except Unauthorized,e:
            """We want this to fail"""
        
        try:
            if str(self.portal.portal_membership.getAuthenticatedMember())=='Anonymous User':
                raise Unauthorized
            else:
                self.testfile.setTitle('test Title')
                self.testfile.setExcludeFromNav(False)
                self.testfile.setDescription('test Image')
                self.testfile.setFile(None)
                IAnnotations(self.testfile)['educommons.clearcopyright'] = 1
                raise 'An anonymous user should not be allowed to edit files.'  
        except Unauthorized,e:
            """We want this to fail"""

   

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(testObjectEdit))
    return suite

