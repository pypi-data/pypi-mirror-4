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

import unittest
from zope.component import getUtility
from base import eduCommonsTestCase


class TestRSS(eduCommonsTestCase):

    def test_is_part_of(self):
        """ Ensure that the right parent is returned when assigning dcterms:isPartOf """
        
        self.setRoles('Manager')
        self.dept = self.addTestDepartment(id='dept')
        self.course = self.addTestCourse(id='course',context=self.dept)
        self.document = self.addTestDocument('resource', context=self.course)
        
        portal = self.portal        

        #test Dept
        obj_type, obj_url = portal.dept.restrictedTraverse('rss').isPartOf(self.dept)        
        #Expects 'Plone Site' as parent
        self.failUnlessEqual(obj_type, portal.Type())
        #Expects portal url as parent_url
        self.failUnlessEqual(obj_url, portal.absolute_url())
        
        #test Course
        obj_type, obj_url = portal.dept.course.restrictedTraverse('rss').isPartOf(self.course)        
        #Expects 'Course' as parent, else ec:metadata won't be expressed
        self.failUnlessEqual(obj_type, self.course.Type())
        #Expects dept as parent_url
        self.failUnlessEqual(obj_url, self.dept.absolute_url())
    
        #test Document
        obj_type, obj_url = portal.dept.course.restrictedTraverse('rss').isPartOf(self.document)        
        #Expects 'Course' as parent, else ec:metadata won't be expressed
        self.failUnlessEqual(obj_type, self.course.Type())
        #Expects course as parent_url
        self.failUnlessEqual(obj_url, self.course.absolute_url())


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestRSS))
    return suite
