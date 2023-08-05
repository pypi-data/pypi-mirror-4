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
import os, sys

class NewTest(unittest.TestCase):
    def setUp(self):
	
        self.verificationErrors = []
	self.selenium = selenium("localhost",port, browser,url,instance)
#	self.selenium = selenium("localhost", 4444, "*chrome", "http://localhost:8080/eduCommons/login_form")
        self.selenium.start()
    
    def test_new_Header(self):
        sel = self.selenium
        sel.open("/eduCommons")
	sel.login("admin","test1234")
	sel.open("/eduCommons/@@leftskin-controlpanel")
    sel.click("//a[@id='fieldsetlegend-leftSkinHeaderSchema']/span")
   	sel.type("form.portal_banner","test_headerBackground.png.jpeg")
	sel.click("form.actions.save")
	sel.wait_for_page_to_load("30000")
	
	

    def test_new_defult(self):
        sel = self.selenium
        sel.open("/eduCommons")
	sel.login("admin","test1234")
	#sel.open("http://localhost:8080/eduCommons/headerBackground.png")
	
	sel.open("/eduCommons/@@leftskin-controlpanel")
        sel.click("//a[@id='fieldsetlegend-leftSkinHeaderSchema']/span")
	
	sel.click("form.actions.Reset to Default")
	

    def tearDown(self):
        self.selenium.stop()
        self.assertEqual([], self.verificationErrors)

if __name__ == "__main__":
    unittest.main()
