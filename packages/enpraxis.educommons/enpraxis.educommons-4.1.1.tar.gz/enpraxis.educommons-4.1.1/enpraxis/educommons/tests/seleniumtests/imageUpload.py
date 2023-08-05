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

#this creates and image and imports it on a page
from seleniumWrapper import selenium
import os, sys
import unittest, time, re
import unittest
import random
import time


class NewTest(unittest.TestCase):
    def setUp(self):
        self.verificationErrors = []
        self.selenium = selenium("localhost",port, browser,url,instance)
        self.selenium.start()
    
    def test_new_image(self):
        sel = self.selenium
        sel.open("/eduCommons/@@coursebuilderform")
	sel.login("admin","test1234")
        sel.click('//span[contains(text(),"Add new")]')
        sel.click("image")
        sel.wait_for_page_to_load("30000")
        sel.type("title", "Test Image")
        sel.type("description", "description text")
        sel.type("image_file", os.path.join(os.path.dirname(__file__),"flower.jpg"))
        sel.click("form_submit")
        sel.wait_for_page_to_load("30000")
	#check
	self.failUnless(sel.is_text_present("28.3 kB"))

    def test_new_page(self):
        sel = self.selenium
        sel.open("/eduCommons/@@coursebuilderform")
	sel.login("admin","test1234")
        sel.click('//span[contains(text(),"Add new")]')
        sel.click('//span[@class="subMenuTitle" and text() = "Page"]')
        sel.wait_for_page_to_load("30000")   
	sel.type("title", "Test Image"+ str(random.randint(1111,9999)))
	sel.type("description", "asdfasdf")
	#sel.click("kupu-imagelibdrawer-button")
	#sel.click("document.forms[1].elements[52]")
	#import pdb;pdb.set_trace()  
        #sel.click("document.forms[1].elements[34]")
	sel.click("kupu-source-button")
        sel.type("text", "<img src=\"test-image\">")
	sel.click("form_submit")
	sel.wait_for_page_to_load("30000")
	#checks
	self.failUnless(sel.is_element_present("//div[@id='parent-fieldname-text']/img"))
    
    def tearDown(self):
        self.selenium.stop()
        self.assertEqual([], self.verificationErrors)

if __name__ == "__main__":
    unittest.main()
