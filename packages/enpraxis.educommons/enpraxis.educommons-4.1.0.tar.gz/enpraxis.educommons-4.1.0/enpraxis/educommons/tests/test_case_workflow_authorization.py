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

class testWorkflowAuthorization(eduCommonsTestCase):

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


    def testContentObjectsWithQA(self):
        self._testContentObjectAsQA(obj=self.document)
        self._testContentObjectAsQA(obj=self.file)
        self._testContentObjectAsQA(obj=self.image)
    
    def _testContentObjectAsQA(self,obj=None):
        """ This method tests what a QA can do and not what they cannot do"""
        #login as admin    
        self.setRoles('Administrator')
        
        if 'InProgress' == self.workflow.getInfoFor(obj,'review_state'):
            self.workflow.doActionFor(obj,'submit')
        self.assertEqual(self.workflow.getInfoFor(obj,'review_state'),'QA')
        
        #login as the QA user
        self.setRoles('QA')
        self.workflow.doActionFor(obj,'release')
        self.assertEqual(self.workflow.getInfoFor(obj,'review_state'),'Released')
    
    def testContentObjectsWithPublisher(self):
        self._testContentObjectAsPublisher(obj=self.document)
        self._testContentObjectAsPublisher(obj=self.file)
        self._testContentObjectAsPublisher(obj=self.image)

    def _testContentObjectAsPublisher(self,obj=None):
        """This method tests what a publisher can and cannot do"""
        #login as admin    
        self.setRoles('Administrator')
        #put the document in the QA state
        if 'InProgress' == self.workflow.getInfoFor(obj,'review_state'):
            self.workflow.doActionFor(obj,'submit')
        if 'QA' == self.workflow.getInfoFor(obj,'review_state'):
            self.workflow.doActionFor(obj,'release')
    
        self.assertEqual(self.workflow.getInfoFor(obj,'review_state'),'Released')
        
        #login as the Publisher user
        self.setRoles('Publisher')
        self.workflow.doActionFor(obj,'publish')
        self.assertEqual(self.workflow.getInfoFor(obj,'review_state'),'Published')
    
    #This method tests what a viewer can do and not what they cannot do
    def testDocumentWithViewer(self):
        """Viewers cannot do anything with the workflow"""
    
    #This method tests what an owner can do and not what they cannot do
    def testDocumentWithOwner(self):
        """Owners cannot do anything with the workflow"""   

    def testContentObjectsWithProducer(self):
        self._testContentObjectAsProducer(obj=self.document)
        self._testContentObjectAsProducer(obj=self.file)
        self._testContentObjectAsProducer(obj=self.image)
    
    #This method tests what actions a producer can do and not what they cannot do
    def _testContentObjectAsProducer(self,obj=None):
        #login as admin    
        self.setRoles('Administrator')       
 
        #clear copyright 
        self.setRoles('Producer')
        self.assertEqual(self.workflow.getInfoFor(obj,'review_state'),'InProgress')

        #sumbit to QA
        self.workflow.doActionFor(obj,'submit')
        self.assertEqual(self.workflow.getInfoFor(obj,'review_state'),'QA')

        #producer should not be able to move the document any further
        #use the workflow tool to determine what actions are being allowed at this point        
        transitions = self.workflow.getTransitionsFor(obj=obj)
        #Make sure there is only the add comment transition
        self.assertEqual(len(transitions),1)
        transition = transitions[0]
        self.assertEqual(transition['id'],'addComment') 


    def testContentObjectsWithProducer(self):
        self._testContentObjectAsAdministrator(obj=self.document)
        self._testContentObjectAsAdministrator(obj=self.image)
        self._testContentObjectAsAdministrator(obj=self.file)

    #This method tests what an administrator can do and not what they cannot do
    def _testContentObjectAsAdministrator(self,obj=None):
        #administrator clear copyright 
        self.setRoles('Administrator')

        #administrator sumbit to QA
        self.assertEqual(self.workflow.getInfoFor(obj,'review_state'),'InProgress')
        self.workflow.doActionFor(obj,'submit')
        self.assertEqual(self.workflow.getInfoFor(obj,'review_state'),'QA')

        #use the workflow tool to determine what actions are being allowed at this point        
        transitions = self.workflow.getTransitionsFor(obj=obj)
    
        #Make sure the following transitions exist
        checklist = {} 
        checklist['release'] = 0
        checklist['reviewer_rework'] = 0
        checklist['addComment'] = 0
        for transition in transitions:
            checklist[transition['id']] = 1
        self.assertEqual(checklist['release'],1)    
        self.assertEqual(checklist['reviewer_rework'],1) 
        self.assertEqual(checklist['addComment'],1)

        #send to released and then back to qa
        self.workflow.doActionFor(obj,'release')
        self.assertEqual(self.workflow.getInfoFor(obj,'review_state'),'Released')       
        self.workflow.doActionFor(obj,'publisher_rework')
        self.assertEqual(self.workflow.getInfoFor(obj,'review_state'),'InProgress')     
        self.workflow.doActionFor(obj,'submit')
        self.assertEqual(self.workflow.getInfoFor(obj,'review_state'),'QA')

        #send to inprogress and then back to qa
        self.workflow.doActionFor(obj,'reviewer_rework')
        self.assertEqual(self.workflow.getInfoFor(obj,'review_state'),'InProgress')     
        self.workflow.doActionFor(obj,'submit')
        self.assertEqual(self.workflow.getInfoFor(obj,'review_state'),'QA')
    
        #move to the released state
        self.workflow.doActionFor(obj,'release')
        self.assertEqual(self.workflow.getInfoFor(obj,'review_state'),'Released')       
    
        transitions = self.workflow.getTransitionsFor(obj=obj)
        #Make sure the following transitions exist
        checklist = {} 
        checklist['publish'] = 0
        checklist['publisher_rework'] = 0
        checklist['addComment'] = 0
        checklist['publisher_retest'] = 0
    
        for transition in transitions:
            checklist[transition['id']] = 1

        self.assertEqual(checklist['publish'],1)    
        self.assertEqual(checklist['publisher_rework'],1)    
        self.assertEqual(checklist['addComment'],1)
        self.assertEqual(checklist['publisher_retest'],1)

        #send to published and then back to Released
        self.workflow.doActionFor(obj,'publish')
        self.assertEqual(self.workflow.getInfoFor(obj,'review_state'),'Published')  
        self.workflow.doActionFor(obj,'manager_rework')
        self.assertEqual(self.workflow.getInfoFor(obj,'review_state'),'InProgress')
        self.workflow.doActionFor(obj,'submit')
        self.assertEqual(self.workflow.getInfoFor(obj,'review_state'),'QA')
        self.workflow.doActionFor(obj,'release')
        self.assertEqual(self.workflow.getInfoFor(obj,'review_state'),'Released')       

        #send to copyright and then back to Released
        self.workflow.doActionFor(obj,'publisher_rework')
        self.assertEqual(self.workflow.getInfoFor(obj,'review_state'),'InProgress')     
        self.workflow.doActionFor(obj,'submit')
        self.assertEqual(self.workflow.getInfoFor(obj,'review_state'),'QA')
        self.workflow.doActionFor(obj,'release')
        self.assertEqual(self.workflow.getInfoFor(obj,'review_state'),'Released')       

        #send to InProgress and then back to Released
        self.workflow.doActionFor(obj,'publisher_rework')
        self.assertEqual(self.workflow.getInfoFor(obj,'review_state'),'InProgress')     
        self.workflow.doActionFor(obj,'submit')
        self.assertEqual(self.workflow.getInfoFor(obj,'review_state'),'QA')
        self.workflow.doActionFor(obj,'release')
        self.assertEqual(self.workflow.getInfoFor(obj,'review_state'),'Released')       

        #send to InProgress and then back to Released
        self.workflow.doActionFor(obj,'publisher_retest')
        self.assertEqual(self.workflow.getInfoFor(obj,'review_state'),'QA')
        self.workflow.doActionFor(obj,'release')
        self.assertEqual(self.workflow.getInfoFor(obj,'review_state'),'Released')       

        self.workflow.doActionFor(obj,'publish')
        self.assertEqual(self.workflow.getInfoFor(obj,'review_state'),'Published')  
        transitions = self.workflow.getTransitionsFor(obj=obj)
        #Make sure the following transitions exist
        checklist = {} 
        checklist['manager_rework'] = 0
        checklist['addComment'] = 0
    
        for transition in transitions:
            checklist[transition['id']] = 1

        self.assertEqual(checklist['manager_rework'],1)  
        self.assertEqual(checklist['addComment'],1)

        #send to copyright and then back to Published 
        self.workflow.doActionFor(obj,'manager_rework')
        self.assertEqual(self.workflow.getInfoFor(obj,'review_state'),'InProgress')     
        self.workflow.doActionFor(obj,'submit')
        self.assertEqual(self.workflow.getInfoFor(obj,'review_state'),'QA')
        self.workflow.doActionFor(obj,'release')
        self.assertEqual(self.workflow.getInfoFor(obj,'review_state'),'Released')       
        self.workflow.doActionFor(obj,'publish')
        self.assertEqual(self.workflow.getInfoFor(obj,'review_state'),'Published')  
    
        #send to in progress and then back to Published 
        self.workflow.doActionFor(obj,'manager_rework')
        self.assertEqual(self.workflow.getInfoFor(obj,'review_state'),'InProgress')     
        self.workflow.doActionFor(obj,'submit')
        self.assertEqual(self.workflow.getInfoFor(obj,'review_state'),'QA')
        self.workflow.doActionFor(obj,'release')
        self.assertEqual(self.workflow.getInfoFor(obj,'review_state'),'Released')       
        self.workflow.doActionFor(obj,'publish')
        self.assertEqual(self.workflow.getInfoFor(obj,'review_state'),'Published')  

    
    def testCourseObjectsAsQA(self):
        """This method tests what a QA can and cannot do"""
        #login as admin    
        self.setRoles('Administrator')
        #make sure the department is in the qa state so the qa user can attempt to move it  
        obj = self.department
        if 'InProgress' == self.workflow.getInfoFor(self.department,'review_state'):
           self.workflow.doActionFor(obj,'submit')
    
        self.assertEqual(self.workflow.getInfoFor(obj,'review_state'),'QA')
        
        #login as the QA user
        self.setRoles('QA')
        self.workflow.doActionFor(obj,'release')
        
        #the qa user should also be able to rework a department
        #login as admin
        self.setRoles('Administrator')
        self.workflow.doActionFor(obj,'publisher_retest')
        self.assertEqual(self.workflow.getInfoFor(self.department,'review_state'),'QA')
    
        #login as the QA user
        self.setRoles('QA')
        self.workflow.doActionFor(obj,'reviewer_rework')
        self.assertEqual(self.workflow.getInfoFor(self.department,'review_state'),'InProgress')
    

        #now attempt to move the course from the qa state into the released state

        #login as admin    
        self.setRoles('Administrator') 
        #make sure the course is in the qa state so the qa user can attempt to move it  
    
        if 'InProgress' == self.workflow.getInfoFor(self.course,'review_state'):
            self.workflow.doActionFor(self.course,'submit')
    
        self.assertEqual(self.workflow.getInfoFor(self.course,'review_state'),'QA')
        
        #login as the QA user
        self.setRoles('QA')
        self.workflow.doActionFor(self.course,'release')
        self.assertEqual(self.workflow.getInfoFor(self.course,'review_state'),'Released')

        #The qa user should also be able to rework a course
        self.setRoles('Administrator')
        self.workflow.doActionFor(self.course,'publisher_retest')
        self.assertEqual(self.workflow.getInfoFor(self.course,'review_state'),'QA')

        #login as the QA user
        self.setRoles('QA')
        self.workflow.doActionFor(self.course,'reviewer_rework')
        self.assertEqual(self.workflow.getInfoFor(self.course,'review_state'),'InProgress')

    def testCourseObjectsAsProducer(self):
        """This method tests what a producer can do"""
        #login as the Producer user
        self.setRoles('Producer')   
 
        #move the department from the in-progress to qa state 
        self.assertEqual(self.workflow.getInfoFor(self.department,'review_state'),'InProgress')
        
        self.workflow.doActionFor(self.department,'submit')
        self.assertEqual(self.workflow.getInfoFor(self.department,'review_state'),'QA')
    
        #now attempt to move the course from the in progress to the qa state 
        self.assertEqual(self.workflow.getInfoFor(self.course,'review_state'),'InProgress')
        self.workflow.doActionFor(self.course,'submit')
        self.assertEqual(self.workflow.getInfoFor(self.course,'review_state'),'QA')

    def testCourseObjectsAsPublisher(self):
        """This method tests what a Publisher can and cannot do"""
        #login as the Administrator user
        self.setRoles('Administrator')

        self.assertEqual(self.workflow.getInfoFor(self.department,'review_state'),'InProgress')
        self.workflow.doActionFor(self.department,'submit')
        self.assertEqual(self.workflow.getInfoFor(self.department,'review_state'),'QA')
        self.workflow.doActionFor(self.department,'release')
        self.assertEqual(self.workflow.getInfoFor(self.department,'review_state'),'Released')
    
        self.assertEqual(self.workflow.getInfoFor(self.course,'review_state'),'InProgress')
        self.workflow.doActionFor(self.course,'submit')
        self.assertEqual(self.workflow.getInfoFor(self.course,'review_state'),'QA')
        self.workflow.doActionFor(self.course,'release')
        self.assertEqual(self.workflow.getInfoFor(self.course,'review_state'),'Released')

        #login as the Publisher user
        self.setRoles('Publisher')

        #now publish the department
        self.workflow.doActionFor(self.department,'publish')
        self.assertEqual(self.workflow.getInfoFor(self.department,'review_state'),'Published')

        #login as admin and put the object in the released state
        self.setRoles('Administrator')

        self.assertEqual(self.workflow.getInfoFor(self.department,'review_state'),'Published')
        self.workflow.doActionFor(self.department,'manager_rework')
        self.assertEqual(self.workflow.getInfoFor(self.department,'review_state'),'InProgress')
        self.workflow.doActionFor(self.department,'submit')
        self.assertEqual(self.workflow.getInfoFor(self.department,'review_state'),'QA')
        self.workflow.doActionFor(self.department,'release')
        self.assertEqual(self.workflow.getInfoFor(self.department,'review_state'),'Released')
        
        #login as the Publisher user and push object to QA
        self.setRoles('Publisher')

        self.workflow.doActionFor(self.department,'publisher_retest')
        self.assertEqual(self.workflow.getInfoFor(self.department,'review_state'),'QA')

        #login as admin and put the self.department back in the released state
        self.setRoles('Administrator')

        self.workflow.doActionFor(self.department,'release')
        self.assertEqual(self.workflow.getInfoFor(self.department,'review_state'),'Released')

        #login as the Publisher user and push object to InProgress state
        self.setRoles('Publisher')

        self.workflow.doActionFor(self.department,'publisher_rework')
        self.assertEqual(self.workflow.getInfoFor(self.department,'review_state'),'InProgress')

        #now publish the course 
        self.workflow.doActionFor(self.course,'publish')
        self.assertEqual(self.workflow.getInfoFor(self.course,'review_state'),'Published')
    
        #publisher should be able to send a course for rework or publisher_retest
        #login as admin and put the object in the released state
        self.setRoles('Administrator')
        
        self.workflow.doActionFor(self.course,'manager_rework')
        self.assertEqual(self.workflow.getInfoFor(self.course,'review_state'),'InProgress')
        self.workflow.doActionFor(self.course,'submit')
        self.assertEqual(self.workflow.getInfoFor(self.course,'review_state'),'QA')
        self.workflow.doActionFor(self.course,'release')
        self.assertEqual(self.workflow.getInfoFor(self.course,'review_state'),'Released')
        
        #login as the Publisher user and push object to QA
        self.setRoles('Publisher')

        self.workflow.doActionFor(self.course,'publisher_retest')
        self.assertEqual(self.workflow.getInfoFor(self.course,'review_state'),'QA')

        #login as admin and put the course back in the released state
        self.setRoles('Administrator')
        self.workflow.doActionFor(self.course,'release')
        self.assertEqual(self.workflow.getInfoFor(self.course,'review_state'),'Released')

        #login as the Publisher user and push object to InProgress state
        self.setRoles('Publisher')
        self.workflow.doActionFor(self.course,'publisher_rework')
        self.assertEqual(self.workflow.getInfoFor(self.course,'review_state'),'InProgress')


    def testCourseObjectsAsAdministrator(self):
        """This method tests what a Publisher can do """
        #login as the Administrator user
        self.setRoles('Administrator')

        self.assertEqual(self.workflow.getInfoFor(self.department,'review_state'),'InProgress')
        self.workflow.doActionFor(self.department,'submit')
        self.assertEqual(self.workflow.getInfoFor(self.department,'review_state'),'QA')
        self.workflow.doActionFor(self.department,'release')
        self.assertEqual(self.workflow.getInfoFor(self.department,'review_state'),'Released')
        self.workflow.doActionFor(self.department,'publish')
        self.assertEqual(self.workflow.getInfoFor(self.department,'review_state'),'Published')
        #now reverse the workflow
    
        self.workflow.doActionFor(self.department,'manager_rework')
        self.assertEqual(self.workflow.getInfoFor(self.department,'review_state'),'InProgress')
        self.workflow.doActionFor(self.department,'submit')
        self.workflow.doActionFor(self.department,'release')
        self.workflow.doActionFor(self.department,'publisher_retest')
        self.assertEqual(self.workflow.getInfoFor(self.department,'review_state'),'QA')
        self.workflow.doActionFor(self.department,'reviewer_rework')
        self.assertEqual(self.workflow.getInfoFor(self.department,'review_state'),'InProgress')

        #now test the self.course object
    
        self.assertEqual(self.workflow.getInfoFor(self.course,'review_state'),'InProgress')
        self.workflow.doActionFor(self.course,'submit')
        self.assertEqual(self.workflow.getInfoFor(self.course,'review_state'),'QA')
        self.workflow.doActionFor(self.course,'release')
        self.assertEqual(self.workflow.getInfoFor(self.course,'review_state'),'Released')
        self.workflow.doActionFor(self.course,'publish')
        self.assertEqual(self.workflow.getInfoFor(self.course,'review_state'),'Published')
    
        #now reverse the workflow
        self.workflow.doActionFor(self.course,'manager_rework')
        self.assertEqual(self.workflow.getInfoFor(self.course,'review_state'),'InProgress')
        self.workflow.doActionFor(self.course,'submit')
        self.workflow.doActionFor(self.course,'release')
        self.workflow.doActionFor(self.course,'publisher_retest')
        self.assertEqual(self.workflow.getInfoFor(self.course,'review_state'),'QA')
        self.workflow.doActionFor(self.course,'reviewer_rework')
        self.assertEqual(self.workflow.getInfoFor(self.course,'review_state'),'InProgress')

    #This method is designed to test not permitted workflow actions with Course Objects (Departments and Courses)
    def testNotAllowedCourseRepositoryWorkflowActions(self):
        self._testNotAllowedDepartmentActions(id='Department')    
        self._testNotAllowedCourseActions(dep='Department',id='Course')
    
    def _testNotAllowedDepartmentActions(self,id=None):
        obj = self.department 

        #The following users should not be allowed to do anything in the InProgress state: 
        #   Owner, Viewer, Anonymous, Publisher, QA
        if 'InProgress' == self.workflow.getInfoFor(self.department,'review_state'):
        
            #login as Anonymous user    
            self.logout()
            self.verifyTransitionSet(obj)
            #Owner
            self.login(user_name)
            self.setRoles('Owner')
            #Viewer
            self.setRoles('Viewer')
            self.verifyTransitionSet(obj)
            #Publisher
            self.setRoles('Publisher')
            self.verifyTransitionSet(obj)
            #QA
            self.setRoles('QA')
            self.verifyTransitionSet(obj)
        
            #Login as the producer and make sure the only transistions the producer has is add comment, submit
            self.setRoles('Producer')
            transitions = self.workflow.getTransitionsFor(obj=obj)
            if len(transitions)==2:
                checklist = {} 
                checklist['submit'] = 0
                checklist['addComment'] = 0
                for transition in transitions:
                    checklist[transition['id']] = 1
                self.assertEqual(checklist['submit'],1) 
                self.assertEqual(checklist['addComment'],1)
            else :
                raise 'This producer does not have the correct number and/or type of transitions'
        
            #Login as the administrator and move the object to the copyright state
            self.setRoles('Administrator')
            self.workflow.doActionFor(self.department,'submit')
            self.assertEqual(self.workflow.getInfoFor(obj,'review_state'),'QA')
    
        #The following users should not be allowed to do anything in the QA state: 
        #   Owner, Viewer, Anonymous, Producer, Publisher 
        if 'QA' == self.workflow.getInfoFor(obj,'review_state'):
            #login as Anonymous user    
            self.logout()
            self.verifyTransitionSet(obj)
            #Owner
            self.login(user_name)
            self.setRoles('Owner')
            self.verifyTransitionSet(obj)
            #Viewer
            self.setRoles('Viewer')
            self.verifyTransitionSet(obj)
            #Publisher
            self.setRoles('Publisher')
            self.verifyTransitionSet(obj)
            #Producer
            self.setRoles('Producer')
            self.verifyTransitionSet(obj)
        
            #Login as the qa user and make sure the  allowed transitions are correct
            self.setRoles('QA')
            transitions = self.workflow.getTransitionsFor(obj=obj)
            if len(transitions)==3:
                checklist = {} 
                checklist['release'] = 0
                checklist['reviewer_rework'] = 0
                checklist['addComment'] = 0
                for transition in transitions:
                    checklist[transition['id']] = 1
                self.assertEqual(checklist['release'],1)    
                self.assertEqual(checklist['reviewer_rework'],1)
                self.assertEqual(checklist['addComment'],1)
            else :
                raise 'This qa user does not have the correct number and/or type of transitions'
        
            #Login as the administrator and move the object to the copyright state
            self.setRoles('Administrator')
            self.workflow.doActionFor(self.department,'release')            
            self.assertEqual(self.workflow.getInfoFor(obj,'review_state'),'Released')

        #The following users should not be allowed to do anything in the Released state: 
        #   Owner, Viewer, Anonymous, Producer, QA 
        if 'Released' == self.workflow.getInfoFor(obj,'review_state'):
        
            #login as Anonymous user    
            self.logout()
            self.verifyTransitionSet(obj)
            #Owner
            self.login(user_name)
            self.setRoles('Owner')
            self.verifyTransitionSet(obj)
            #Viewer
            self.setRoles('Viewer')
            self.verifyTransitionSet(obj)
            #Producer
            self.setRoles('Producer')
            self.verifyTransitionSet(obj)
            #QA
            self.setRoles('QA')
            self.verifyTransitionSet(obj)
        
            #Login as the publisher and make sure the allowed transistions are correct
            self.setRoles('Publisher')

            transitions = self.workflow.getTransitionsFor(obj=obj)
            if len(transitions)==4:
                checklist = {} 
                checklist['publish'] = 0
                checklist['publisher_retest'] = 0
                checklist['publisher_rework'] = 0
                checklist['addComment'] = 0
                for transition in transitions:
                    checklist[transition['id']] = 1
                self.assertEqual(checklist['publish'],1)    
                self.assertEqual(checklist['publisher_retest'],1)
                self.assertEqual(checklist['publisher_rework'],1)
                self.assertEqual(checklist['addComment'],1)
            else :
                raise 'This publisher does not have the correct number and/or type of transitions'
        
            #Login as the administrator and move the object to the copyright state
            self.setRoles('Administrator')
            self.workflow.doActionFor(self.department,'publish')
            self.assertEqual(self.workflow.getInfoFor(obj,'review_state'),'Published')
    
        #The following users should not be allowed to do anything in the Published state: 
        #   Owner, Viewer, Anonymous, Producer, QA 
        if 'Published' == self.workflow.getInfoFor(obj,'review_state'):
        
            #login as Anonymous user
            self.logout()
            self.verifyTransitionSet(obj)
            #Owner
            self.login(user_name)
            self.setRoles('Owner')
            self.verifyTransitionSet(obj)
            #Viewer
            self.setRoles('Viewer')
            self.verifyTransitionSet(obj)
            #Producer
            self.setRoles('Producer')
            self.verifyTransitionSet(obj)
            #QA
            self.setRoles('QA')
            self.verifyTransitionSet(obj)

            #when an item is published, no one should be allowed to edit it except for manager and admin

    def _testNotAllowedCourseActions(self,dep=None,id=None):
        obj = self.course
 
        #The following users should not be allowed to do anything in the InProgress state: 
        #   Owner, Viewer, Anonymous, Publisher, QA
        if 'InProgress' == self.workflow.getInfoFor(obj,'review_state'):
            
            #login as Anonymous user
            self.logout()
            self.verifyTransitionSet(obj)
            #Owner
            self.login(user_name)
            self.setRoles('Owner')
            self.verifyTransitionSet(obj)
            #Viewer
            self.setRoles('Viewer')
            self.verifyTransitionSet(obj)
            #Publisher
            self.setRoles('Publisher')
            self.verifyTransitionSet(obj)
            #QA
            self.setRoles('QA')
            self.verifyTransitionSet(obj)
        
            #Login as the producer and make sure the only transistions the producer has is add comment, submit, and retract 
            self.setRoles('Producer')

            transitions = self.workflow.getTransitionsFor(obj=obj)
            if len(transitions)==2:
                checklist = {} 
                checklist['submit'] = 0
                checklist['addComment'] = 0
                for transition in transitions:
                    checklist[transition['id']] = 1
                self.assertEqual(checklist['submit'],1) 
                self.assertEqual(checklist['addComment'],1)
            else :
                raise 'This producer does not have the correct number and/or type of transitions'
        
            #Login as the administrator and move the object to the copyright state
            self.setRoles('Administrator')
            self.workflow.doActionFor(obj,'submit')
            self.assertEqual(self.workflow.getInfoFor(obj,'review_state'),'QA')
    
        #The following users should not be allowed to do anything in the QA state: 
        #   Owner, Viewer, Anonymous, Producer, Publisher 
        if 'QA' == self.workflow.getInfoFor(obj,'review_state'):
        
            #login as Anonymous user
            self.logout()
            self.verifyTransitionSet(obj)
            #Owner
            self.login(user_name)
            self.setRoles('Owner')
            self.verifyTransitionSet(obj)
            #Viewer
            self.setRoles('Viewer')
            self.verifyTransitionSet(obj)
            #Publisher
            self.setRoles('Publisher')
            self.verifyTransitionSet(obj)
            #Producer
            self.setRoles('Producer')
            self.verifyTransitionSet(obj)
        
            #Login as the qa user and make sure the  allowed transitions are correct
            self.setRoles('QA')
    
            transitions = self.workflow.getTransitionsFor(obj=obj)
            if len(transitions)==3:
                checklist = {} 
                checklist['release'] = 0
                checklist['reviewer_rework'] = 0
                checklist['addComment'] = 0
                for transition in transitions:
                    checklist[transition['id']] = 1
                self.assertEqual(checklist['release'],1)    
                self.assertEqual(checklist['reviewer_rework'],1)
                self.assertEqual(checklist['addComment'],1)
            else :
                raise 'This qa user does not have the correct number and/or type of transitions'
        
            #Login as the administrator and move the object to the copyright state
            self.setRoles('Administrator')
            self.workflow.doActionFor(obj,'release')
            self.assertEqual(self.workflow.getInfoFor(obj,'review_state'),'Released')

        #The following users should not be allowed to do anything in the Released state: 
        #   Owner, Viewer, Anonymous, Producer, QA 
        if 'Released' == self.workflow.getInfoFor(obj,'review_state'):
        
            #login as Anonymous user
            self.logout()
            self.verifyTransitionSet(obj)
            #Owner
            self.login(user_name)
            self.setRoles('Owner')
            self.verifyTransitionSet(obj)
            #Viewer
            self.setRoles('Viewer')
            self.verifyTransitionSet(obj)
            #QA
            self.setRoles('QA')
            self.verifyTransitionSet(obj)
            #Producer
            self.setRoles('Producer')
            self.verifyTransitionSet(obj)
        
            #Login as the publisher and make sure the allowed transistions are correct
            self.setRoles('Publisher')

            transitions = self.workflow.getTransitionsFor(obj=obj)
            if len(transitions)==4:
                checklist = {} 
                checklist['publish'] = 0
                checklist['publisher_retest'] = 0
                checklist['publisher_rework'] = 0
                checklist['addComment'] = 0
                for transition in transitions:
                    checklist[transition['id']] = 1
                self.assertEqual(checklist['publisher_retest'],1)   
                self.assertEqual(checklist['publish'],1)
                self.assertEqual(checklist['publisher_rework'],1)
                self.assertEqual(checklist['addComment'],1)
            else :
                raise 'This publisher does not have the correct number and/or type of transitions'
        
            #Login as the administrator and move the object to the copyright state
            self.setRoles('Administrator')
            self.workflow.doActionFor(self.course,'publish')
            self.assertEqual(self.workflow.getInfoFor(obj,'review_state'),'Published')
    
        #The following users should not be allowed to do anything in the Published state: 
        #   Owner, Viewer, Anonymous, Producer, QA 
        if 'Published' == self.workflow.getInfoFor(obj,'review_state'):
        
            #login as Anonymous user
            self.logout()
            self.verifyTransitionSet(obj)
            #Owner
            self.login(user_name)
            self.setRoles('Owner')
            self.verifyTransitionSet(obj)
            #Viewer
            self.setRoles('Viewer')
            self.verifyTransitionSet(obj)
            #QA
            self.setRoles('QA')
            self.verifyTransitionSet(obj)
            #Producer
            self.setRoles('Producer')
            self.verifyTransitionSet(obj)

    #This method is designed to test not permitted workflow actions associated with Content
    def testNotAllowedContentActions(self):
        self._testNotAllowedContentActions(obj=self.document)    
        self._testNotAllowedContentActions(obj=self.image)    
        self._testNotAllowedContentActions(obj=self.file)    
    
    def _testNotAllowedContentActions(self,obj=None):
          
        #The following users should not be allowed to do anything in the InProgress state: 
        #   Owner, Viewer, Anonymous, Publisher, QA
        if 'InProgress' == self.workflow.getInfoFor(obj,'review_state'):
        
            #login as Anonymous user
            self.logout()
            self.verifyTransitionSet(obj)
            #Owner
            self.login(user_name)
            self.setRoles('Owner')
            self.verifyTransitionSet(obj)
            #Viewer
            self.setRoles('Viewer')
            self.verifyTransitionSet(obj)
            #QA
            self.setRoles('QA')
            self.verifyTransitionSet(obj)
            #Publisher
            self.setRoles('Publisher')
            self.verifyTransitionSet(obj)
        
            #Login as the producer and make sure the only transistions the producer has is add comment, submit, and retract 
            self.setRoles('Producer')
            transitions = self.workflow.getTransitionsFor(obj=obj)
            if len(transitions)==2:
                checklist = {} 
                checklist['submit'] = 0
                checklist['addComment'] = 0
                for transition in transitions:
                    checklist[transition['id']] = 1
                self.assertEqual(checklist['submit'],1) 
                self.assertEqual(checklist['addComment'],1)
            else :
                raise 'This producer does not have the correct number and/or type of transitions'
        
            #Login as the administrator and move the object to the copyright state
            self.setRoles('Administrator')
            self.workflow.doActionFor(obj,'submit')
            self.assertEqual(self.workflow.getInfoFor(obj,'review_state'),'QA')
    
        #The following users should not be allowed to do anything in the QA state: 
        #   Owner, Viewer, Anonymous, Producer, Publisher 
        if 'QA' == self.workflow.getInfoFor(obj,'review_state'):
        
            #login as Anonymous user
            self.logout()
            self.verifyTransitionSet(obj)
            #Owner
            self.login(user_name)
            self.setRoles('Owner')
            self.verifyTransitionSet(obj)
            #Viewer
            self.setRoles('Viewer')
            self.verifyTransitionSet(obj)
            #Producer
            self.setRoles('Producer')
            self.verifyTransitionSet(obj)
            #Publisher
            self.setRoles('Publisher')
            self.verifyTransitionSet(obj)
        
            #Login as the qa user and make sure the  allowed transitions are correct
            self.setRoles('QA')
   
            transitions = self.workflow.getTransitionsFor(obj=obj)
            if len(transitions)==3:
                checklist = {} 
                checklist['release'] = 0
                checklist['reviewer_rework'] = 0
                checklist['addComment'] = 0
                for transition in transitions:
                    checklist[transition['id']] = 1
                self.assertEqual(checklist['release'],1)
                self.assertEqual(checklist['reviewer_rework'],1)
                self.assertEqual(checklist['addComment'],1)
            else :
                raise 'This qa user does not have the correct number and/or type of transitions'
        
            #Login as the administrator and move the object to the copyright state
            self.setRoles('Administrator')
            self.workflow.doActionFor(obj,'release')
            self.assertEqual(self.workflow.getInfoFor(obj,'review_state'),'Released')

        #The following users should not be allowed to do anything in the Released state: 
        #   Owner, Viewer, Anonymous, Producer, QA 
        if 'Released' == self.workflow.getInfoFor(obj,'review_state'):
        
            #login as Anonymous user
            self.logout()
            self.verifyTransitionSet(obj)
            #Owner
            self.login(user_name)
            self.setRoles('Owner')
            self.verifyTransitionSet(obj)
            #Viewer
            self.setRoles('Viewer')
            self.verifyTransitionSet(obj)
            #Producer
            self.setRoles('Producer')
            self.verifyTransitionSet(obj)
            #QA
            self.setRoles('QA')
            self.verifyTransitionSet(obj)
        
            #Login as the publisher and make sure the allowed transistions are correct
            self.setRoles('Publisher')

            transitions = self.workflow.getTransitionsFor(obj=obj)
            
            if len(transitions)==4:
                checklist = {} 
                checklist['publish'] = 0
                checklist['publisher_rework'] = 0
                checklist['publisher_retest'] = 0
                checklist['addComment'] = 0
                for transition in transitions:
                    checklist[transition['id']] = 1
                self.assertEqual(checklist['publish'],1)    
                self.assertEqual(checklist['publisher_rework'],1)
                self.assertEqual(checklist['publisher_retest'],1)
                self.assertEqual(checklist['addComment'],1)
            else :
                raise 'This publisher does not have the correct number and/or type of transitions'
        
            #Login as the administrator and move the object to the copyright state
            self.setRoles('Administrator')
            self.workflow.doActionFor(obj,'publish')
            self.assertEqual(self.workflow.getInfoFor(obj,'review_state'),'Published')
    
        #The following users should not be allowed to do anything in the Published state: 
        #   Owner, Viewer, Anonymous, Producer, QA 
        if 'Published' == self.workflow.getInfoFor(obj,'review_state'):
        
            #login as Anonymous user
            self.logout()
            self.verifyTransitionSet(obj)
            #Owner
            self.login(user_name)
            self.setRoles('Owner')
            self.verifyTransitionSet(obj)
            #Viewer
            self.setRoles('Viewer')
            self.verifyTransitionSet(obj)
            #Producer
            self.setRoles('Producer')
            self.verifyTransitionSet(obj)
            #QA
            self.setRoles('QA')
            self.verifyTransitionSet(obj)

            #when an item is published, no one should be allowed to edit it except for manager and admin
            #check to make sure this is the case
 

    #This method ensures the only transition allowed is the add comment transition
    def verifyTransitionSet(self,obj=None):
        transitions = self.workflow.getTransitionsFor(obj=obj)
        #Make sure there is only the add comment transition
        if len(transitions)==1:
            transition = transitions[0]
            self.assertEqual(transition['id'],'addComment') 
        elif len(transitions) >1:
            raise 'This user is over the number of allowed transitions'
    
def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(testWorkflowAuthorization))
    return suite
