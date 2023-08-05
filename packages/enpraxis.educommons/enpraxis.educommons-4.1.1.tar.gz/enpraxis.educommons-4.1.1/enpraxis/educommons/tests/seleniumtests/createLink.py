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

#Tests Ticket 578 (http://educommons.com/dev/ticket/578). Looks for Next button -- shouldn't be there.

from seleniumWrapper import selenium
import unittest, time, re
import unittest
import random
import time


class createLink(unittest.TestCase):
    def setUp(self):
	
        self.verificationErrors = []
        #self.selenium = selenium("localhost", 4444, "*chrome", "http://localhost:8080/eduCommons/login_form")
	self.selenium = selenium("localhost",port, browser,url,instance)
        self.selenium.start()

    def test_new_link(self):
        sel = self.selenium
        sel.open("/eduCommons")
	sel.login("admin","test1234")
        sel.click('//span[contains(text(),"Add new")]')
	sel.click('//span[@class="subMenuTitle" and text() = "Link"]')
        sel.wait_for_page_to_load("30000")
        sel.type("title", "next" + str(random.randint(1111,9999)))
	sel.type("description", "next" + str(random.randint(1111,9999)))
	sel.type("remoteUrl", "http://google.com")
	sel.click("form_submit")
	sel.wait_for_page_to_load("30000")
	#import pdb;pdb.set_trace()
	#check
	self.failUnless(sel.is_element_present("link=exact:http://google.com"))

    def tearDown(self):
        self.selenium.stop()
        self.assertEqual([], self.verificationErrors)

if __name__ == "__main__":
    unittest.main()

	
