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
from enpraxis.educommons.browser import SortedResourceListingView, SortedCourseListingView, SortedCrossCourseListingView

class TestSortedResourceListing(eduCommonsTestCase):

    def testSortedListing(self):
        """ test the sorted listing view """

        self.setRoles('Manager')
        self.dept = self.addTestDepartment(id='test-dept')
        self.course1 = self.addTestCourse(id='atest-course',context=self.dept)
        self.addTestDocument('cresource', context=self.course1)
        self.addTestImage(id='aresource', context=self.course1)        
        self.addTestFile(id='bresource', context=self.course1)

        srlv = SortedResourceListingView(self.course1,self.app.REQUEST)
        list = [item.id for item in srlv.getSortedResources()]
        self.failUnlessEqual(list, ['aresource','bresource','cresource'])

    def testCourseListingView(self):
        """ test the course listing view """

        self.setRoles('Manager')
        self.dept = self.addTestDepartment(id='test-dept')
        self.addTestCourse(id='btest-course',context=self.dept)
        self.addTestCourse(id='atest-course',context=self.dept)
        self.addTestCourse(id='gtest-course',context=self.dept)
        self.addTestCourse(id='Atest-course',context=self.dept)

        sclv = SortedCourseListingView(self.portal,self.app.REQUEST)
        list = [item.id for item in sclv.getSortedCourses()]
        self.failUnlessEqual(list, ['btest-course', 'atest-course', 'gtest-course', 'Atest-course'])        

    def testCrossListingView(self):
        """ test the cross listing view """

        self.setRoles('Manager')
        self.dept = self.addTestDepartment(id='test-dept')
        self.course1 = self.addTestCourse(id='btest-course',context=self.dept)
        self.course2 = self.addTestCourse(id='atest-course',context=self.dept)
        self.course3 = self.addTestCourse(id='gtest-course',context=self.dept)
        self.course4 = self.addTestCourse(id='Atest-course',context=self.dept)

        self.course1.crosslisting = ('atest-course',)
        self.course3.crosslisting = ('atest-course',)
        self.course4.crosslisting = ('atest-course',)
        scclv = SortedCrossCourseListingView(self.course2,self.app.REQUEST)
        list = [item.id for item in scclv.getSortedCrossCourses()]
        self.failUnlessEqual(list, ['btest-course', 'gtest-course', 'Atest-course'])            
        
def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestSortedResourceListing))
    return suite
