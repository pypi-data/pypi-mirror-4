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
from Products.CMFCore.utils import getToolByName
from xml.dom import minidom

class testDoubleByteChars(eduCommonsTestCase):
   
    def test_RDFMetadataView(self):

        from enpraxis.educommons.browser import RDFMetadataView
        from xml.dom import minidom

        chin_text = '\xe8\xbf\x99\xe6\x98\xaf\xe6\xb5\x8b\xe8\xaf\x95'
        self.setRoles('Producer')
        dept = self.addTestDepartment()
        course = self.addTestCourse(context=dept )
        course.edit(title=chin_text)
        course.setSubject(chin_text)
        course.setDescription(chin_text)
 
        rdfview = RDFMetadataView(course, self.app.REQUEST)
        data = rdfview.getRDFMetadata(parent=dept)
        self.failUnless(data.find(u'\u8fd9\u662f\u6d4b\u8bd5') != -1)
        doc = minidom.parseString(data.encode('utf-8') )
        subNode = doc.getElementsByTagName('dc:subject')[0].childNodes[0].nodeValue.strip()
        self.failUnless(subNode.find(u'\u8fd9\u662f\u6d4b\u8bd5') != -1)
        subNode = doc.getElementsByTagName('dc:description')[0].childNodes[0].nodeValue.strip()
        self.failUnless(subNode.find(u'\u8fd9\u662f\u6d4b\u8bd5') != -1)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(testDoubleByteChars))
    return suite


