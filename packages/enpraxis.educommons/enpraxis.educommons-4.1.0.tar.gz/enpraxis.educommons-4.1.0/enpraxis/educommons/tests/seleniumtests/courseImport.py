# -*- coding: iso-8859-15 -*-
##################################################################################
#    Copyright (c) 2009 enPraxis, All rights reserved.
#                                                                                
#    This program is free software; you can redistribute it and/or modify        
#    it under the terms of the GNU General Public License as published by        
#    the Free Software Foundation; either version 2 of the License, or           
#    (at your option) any later version.                                         
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

__author__  = '''Zerin Bates'''
__version__   = '$ Revision 0.0 $'[11:-2]

from seleniumWrapper import selenium
import unittest
import random
import time
import os, sys
random_number = str(random.randint(1111,9999))

class PageTest(unittest.TestCase):
    def setUp(self):
        self.verificationErrors = []
        self.selenium = selenium("localhost",port, browser,url,instance)
        # The division will be created in this first test and will be used in the rest
        # of the tests. You can change the following name without breaking the test
        self.divisionTitle = "Test Division " + random_number
        self.courseTitle = "Test Course " + random_number
        self.selenium.start()
    
    def test_course_builder(self):
        # This is a test used for setup, that creates the division and course where
        # we will test all the pages creation.
        sel = self.selenium
        # We login using the wrapped function
        sel.login("admin","test1234")
        # Here the test starts
        sel.click("link=Build a Course")
        sel.wait_for_page_to_load("30000")
        sel.type("form.division.textfield", self.divisionTitle)
        sel.type("form.coursename", self.courseTitle)
        sel.type("form.courseid", "1.0")
        sel.type("form.courseterm", "Testing")
        sel.click("form.actions.Submit")
        sel.wait_for_page_to_load("30000")
        sel.type("description", "Test Desc")
        sel.click("form_submit")
        sel.wait_for_page_to_load("30000")
	
        sel.click("link=Contents")
	
	#sel.wait_for_page_to_load("30000")
        sel.click("@@import_form:method")
	sel.wait_for_page_to_load("30000")
	sel.type("form.filename", os.path.join(os.path.dirname(__file__),"music_course.zip"))
	sel.click("form.actions.import")
	# Checks
	self.failUnless(sel.is_text_present("Syllabus"))
	self.failUnless(sel.is_text_present("Course Schedule"))

    def tearDown(self):
        self.selenium.stop()
        self.assertEqual([], self.verificationErrors)
