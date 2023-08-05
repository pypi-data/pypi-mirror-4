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

"""Unit tests module for the Course content type
"""
import unittest
from mocker import KWARGS
from plone.mocktestcase import MockTestCase

import zope.component

from Products.Archetypes.Schema.factory import instanceSchemaFactory
from Products.Archetypes.utils import DisplayList

from enpraxis.educommons.content.course import Course

class TestCourse(MockTestCase):

    def setUp(self):
        zope.component.provideAdapter(instanceSchemaFactory)
        self.fields = Course.schema.fields()
        self.field_ids = [i.getName() for i in self.fields]
        self.fields_dict = dict(zip(self.field_ids, self.fields))

    def test_getDivisionsVocab(self):
        # brains will be an iterable mocking a searchResults return
        # value.
        brains = []
        brains.append(self.create_dummy(getId='id0', Title='A title'))
        brains.append(self.create_dummy(getId='id1', Title='Another title'))
        brains.append(self.create_dummy(getId='id2', Title='Just another one'))
        brains.append(self.create_dummy(getId='id3', Title='Last title'))
        brains.append(self.create_dummy(getId='id4', Title='Ok, another one'))

        mock_course = self.mocker.patch(Course('id3'))
        self.expect(mock_course.aq_parent.id).result('id3').count(1, 5)
        self.expect(
            mock_course.portal_catalog.searchResults(KWARGS)).result(brains)

        self.replay()

        expected_dl = DisplayList((('None', 'None'),
                                   ('id0', 'A title'),
                                   ('id1', 'Another title'),
                                   ('id2', 'Just another one'),
                                   ('id4', 'Ok, another one'),
                                 ))
        dl = mock_course.getDivisionsVocab()
        self.assertEquals(expected_dl.items(), dl.items())

    def test_getDivisionsVocab_no_divisions(self):
        mock_course = self.mocker.patch(Course('id3'))
        self.expect(mock_course.aq_parent.id).result('id3').count(0)
        self.expect(
            mock_course.portal_catalog.searchResults(KWARGS)).result([])
        self.replay()
        dl = mock_course.getDivisionsVocab()
        self.assertEquals((('None', 'None'),), dl.items())

    def test__at_rename_after_creation(self):
        c = Course('foo')
        self.assertTrue(c._at_rename_after_creation)

    def test_courseId(self):
        c = Course('foo')
        self.failUnless('courseId' in self.field_ids)

        field = self.fields_dict['courseId']
        self.assertTrue(field.getType() == \
            'Products.Archetypes.Field.StringField')


def test_suite():
    """Test suit"""
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestCourse))
    return suite