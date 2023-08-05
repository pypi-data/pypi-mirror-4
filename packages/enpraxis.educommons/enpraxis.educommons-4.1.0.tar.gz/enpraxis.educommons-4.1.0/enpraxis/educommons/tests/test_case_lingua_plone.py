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
from Products.LinguaPlone.tests.utils import makeTranslation
from base import eduCommonsTestCase

class testLinguaPlone(eduCommonsTestCase):

    def afterSetUp(self):
        lang_tool = self.portal.portal_languages
        lang_tool.addSupportedLanguage('de')
        self.setRoles('Producer')
        self.portal.invokeFactory('Division', 'testDepartment')
        self.portal.testDepartment.invokeFactory('Course', 'testCourse')
        self.portal.testDepartment.testCourse.invokeFactory('Document', 'testDocument')
        self.portal.testDepartment.testCourse.invokeFactory('File', 'testFile')
        self.portal.testDepartment.testCourse.invokeFactory('Image', 'testImage')

    def testObjectsLocalizable(self):
        self.de_dept = makeTranslation(self.portal.testDepartment, 'de')
        self.assertEqual(self.de_dept.isTranslation(), True)
        
        self.de_course = makeTranslation(self.portal.testDepartment.testCourse, 'de')
        self.assertEqual(self.de_course.isTranslation(), True)
        
        self.de_doc = makeTranslation(self.portal.testDepartment.testCourse.testDocument, 'de')
        self.assertEqual(self.de_doc.isTranslation(), True)
        
        self.de_file = makeTranslation(self.portal.testDepartment.testCourse.testFile, 'de')
        self.assertEqual(self.de_file.isTranslation(), True)
        
        self.de_image = makeTranslation(self.portal.testDepartment.testCourse.testImage, 'de')
        self.assertEqual(self.de_image.isTranslation(), True)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(testLinguaPlone))
    return suite
