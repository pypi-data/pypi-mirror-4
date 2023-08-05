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

from Products.CMFCore.utils import getToolByName
from Products.PloneTestCase.PloneTestCase import PloneTestCase
from Products.CMFPlone.tests.dummy import Dummy
from zope.annotation.interfaces import IAnnotations
from zope.interface import alsoProvides
from enpraxis.educommons.browser import PositionView
from zope.testing import doctest
from plone.mocktestcase import MockTestCase
from base import eduCommonsTestCase

class testOrdering(eduCommonsTestCase):


    def afterSetUp(self):
        self.setRoles('Producer')
        self.course = self.addTestCourse(context=self.addTestDepartment())
        self.doc1 = self.addTestDocument(id='doc1',context=self.course)
        self.doc2 = self.addTestDocument(id='doc2',context=self.course)
        self.doc3 = self.addTestDocument(id='doc3',context=self.course)

    def test_swapPosition(self):

        IAnnotations(self.doc1)['eduCommons.objPositionInCourse'] = 1
        IAnnotations(self.doc2)['eduCommons.objPositionInCourse'] = 2
        IAnnotations(self.doc3)['eduCommons.objPositionInCourse'] = 3
        self.doc1.reindexObject()
        self.doc2.reindexObject()
        self.doc3.reindexObject()

        self.course.request = self.app.REQUEST
        pos_view = PositionView(self.course,self.app.REQUEST)
        pos_view.swapPosition(self.doc1,self.doc2)
        
        # Verify that portal_catalog matches the annotations on the object
        cat = self.portal.portal_catalog
        self.assertEqual(cat.searchResults(path={'query':'/'.join(self.doc1.getPhysicalPath())})[0].getObjPositionInCourse,IAnnotations(self.doc1)['eduCommons.objPositionInCourse'])
        self.assertEqual(cat.searchResults(path={'query':'/'.join(self.doc2.getPhysicalPath())})[0].getObjPositionInCourse,IAnnotations(self.doc2)['eduCommons.objPositionInCourse'])

    def test_moveUp(self):

        IAnnotations(self.doc1)['eduCommons.objPositionInCourse'] = 1
        IAnnotations(self.doc2)['eduCommons.objPositionInCourse'] = 2
        IAnnotations(self.doc3)['eduCommons.objPositionInCourse'] = 3
        self.doc1.reindexObject()
        self.doc2.reindexObject()
        self.doc3.reindexObject()

        self.course.request = self.app.REQUEST
        pos_view = PositionView(self.course,self.app.REQUEST)
        pos_view.moveUp(self.course,0,'','/'.join(self.doc3.getPhysicalPath()) )

        # Verify that portal_catalog matches the annotations on the object
        cat = self.portal.portal_catalog
        self.assertEqual(cat.searchResults(path={'query':'/'.join(self.doc1.getPhysicalPath())})[0].getObjPositionInCourse,IAnnotations(self.doc1)['eduCommons.objPositionInCourse'])
        self.assertEqual(cat.searchResults(path={'query':'/'.join(self.doc2.getPhysicalPath())})[0].getObjPositionInCourse,IAnnotations(self.doc2)['eduCommons.objPositionInCourse'])
        self.assertEqual(cat.searchResults(path={'query':'/'.join(self.doc3.getPhysicalPath())})[0].getObjPositionInCourse,IAnnotations(self.doc3)['eduCommons.objPositionInCourse'])

    def test_moveDown(self):

        IAnnotations(self.doc1)['eduCommons.objPositionInCourse'] = 1
        IAnnotations(self.doc2)['eduCommons.objPositionInCourse'] = 2
        IAnnotations(self.doc3)['eduCommons.objPositionInCourse'] = 3
        self.doc1.reindexObject()
        self.doc2.reindexObject()
        self.doc3.reindexObject()

        self.course.request = self.app.REQUEST
        pos_view = PositionView(self.course,self.app.REQUEST)
        pos_view.moveDown(self.course,0,'','/'.join(self.doc1.getPhysicalPath()) )

        # Verify that portal_catalog matches the annotations on the object
        cat = self.portal.portal_catalog
        self.assertEqual(cat.searchResults(path={'query':'/'.join(self.doc1.getPhysicalPath())})[0].getObjPositionInCourse,IAnnotations(self.doc1)['eduCommons.objPositionInCourse'])
        self.assertEqual(cat.searchResults(path={'query':'/'.join(self.doc2.getPhysicalPath())})[0].getObjPositionInCourse,IAnnotations(self.doc2)['eduCommons.objPositionInCourse'])
        self.assertEqual(cat.searchResults(path={'query':'/'.join(self.doc3.getPhysicalPath())})[0].getObjPositionInCourse,IAnnotations(self.doc3)['eduCommons.objPositionInCourse'])

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(testOrdering))
    return suite


