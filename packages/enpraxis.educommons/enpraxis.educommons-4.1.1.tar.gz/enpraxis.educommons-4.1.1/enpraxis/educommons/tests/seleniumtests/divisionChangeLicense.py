# -*- coding: iso-8859-15 -*-
##################################################################################
#    Copyright (c) 2009 enPraxis, All rights reserved.
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

__author__  = '''Zerin Bates'''
__version__   = '$ Revision 0.0 $'[11:-2]
# -*- coding: iso-8859-15 -*-
#this test creates a division and a page and changes the divisions ownership and license
from seleniumWrapper import selenium
import unittest
import random
import time
# This number is used for the division and course title created in this test
random_number = str(random.randint(1111,9999))

class PageTest(unittest.TestCase):
    def setUp(self):
        self.verificationErrors = []
        self.selenium = selenium("localhost",port, browser,url,instance)
        self.divisionTitle = "Test Division " + random_number
        self.courseTitle = "Test Course " + random_number
        self.selenium.start()
    

    def test_new_page(self):
	unicodeString = u"page something or other"
	pageTitle = "monty" + str(random.randint(1111,9999))
	sel = self.selenium

	sel.login("admin","test1234")
#	i add division
	sel.click('//span[contains(text(),"Add new")]')
	sel.click('//span[@class="subMenuTitle" and text() = "Division"]')
	sel.wait_for_page_to_load("30000")
        
        sel.wait_for_page_to_load("30000")
	sel.type("title", self.courseTitle)
        # i change ownership
        sel.type("description", "Test Desc")
        sel.click("//a[@id='fieldsetlegend-ownership']/span")
        sel.type("creators", "steeve")
        sel.type("contributors", "asdfasdf")
        sel.type("rights", "asdfasdf")
        sel.click("license_2")
        sel.click("recurse_folders")
        sel.click("clearedCopyright")
        sel.click("accessibilitycompliant")
        sel.click("form_submit")
	sel.wait_for_page_to_load("30000")
	# checks license change
	self.failUnless(sel.is_text_present("All Rights Reserved"))
	# i add page
	sel.click('//span[contains(text(),"Add new")]')
	sel.click('//span[@class="subMenuTitle" and text() = "Page"]')
	sel.wait_for_page_to_load("30000")
	sel.type("title",pageTitle)
	sel.type("description", unicodeString + "TestDescription")
	sel.click("kupu-source-button")
	sel.type("text","<p>" + unicodeString + "text</p>")
	sel.click("form_submit")
	sel.wait_for_page_to_load("30000")
	# checks
	
	self.failUnless(sel.is_text_present("Changes saved."))
	self.failUnless(sel.is_text_present("page something or other"))
   
    def tearDown(self):
        self.selenium.stop()
        self.assertEqual([], self.verificationErrors)


