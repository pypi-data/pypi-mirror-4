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
from plone.mocktestcase import MockTestCase
from enpraxis.educommons.browser import ClearCopyrightField
from zope.annotation.interfaces import IAnnotations

class TestUseCourse(MockTestCase):

    def test_get_copyright_true(self):
        obj = self.mocker.mock()
        IAnnotations(obj)
        self.mocker.count(1,None)
        self.mocker.result({'eduCommons.clearcopyright':1})
        self.mocker.replay()
        
        clear_copyright = ClearCopyrightField(context=obj,request=None)
        res1 = clear_copyright.getClearedCopyright()
        self.failUnlessEqual(res1,1)
    
    def test_get_copyright_false(self):
        obj = self.mocker.mock()
        IAnnotations(obj)
        self.mocker.count(1,None)
        self.mocker.result({'eduCommons.clearcopyright':0})
        self.mocker.replay()
        
        clear_copyright = ClearCopyrightField(context=obj,request=None)
        res1 = clear_copyright.getClearedCopyright()
        self.failUnlessEqual(res1,0)


    def test_reusecourseportlet_renderer(self):

        from Products.CMFPlone.tests.dummy import Dummy
        
        dummy = Dummy()
        wfdummy = Dummy()
        wfdummy.getInfoFor = lambda x,y: 'Published'
        dummy.id = 'course1'
        dummy.portal_workflow = wfdummy
        setattr(dummy,'course1.zip',None)
        dummy.Type = lambda: 'Course'

        obj_mock = self.mocker.mock()
        self.expect(obj_mock.ecparent).result(dummy)
        self.mocker.count(1,None)
        self.mocker.replay()

        from enpraxis.educommons.portlet.reusecourseportlet import Renderer
        avfunc = Renderer.available        
        val = avfunc.fget(obj_mock)
        self.failUnlessEqual(val,True)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestUseCourse))
    return suite
