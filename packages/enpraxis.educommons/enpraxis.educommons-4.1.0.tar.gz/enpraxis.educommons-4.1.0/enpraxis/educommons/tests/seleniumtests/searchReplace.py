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

__author__  = '''Tom Caswell'''
__version__   = '$ Revision 0.0 $'[11:-2]

#creates a new eduCommons instance

from seleniumWrapper import selenium
import unittest, time, re
import unittest
import time
class SearchReplaceTest(unittest.TestCase):
    def setUp(self):
        self.verificationErrors = []
        self.selenium = selenium("localhost",port, browser,url,instance)
        self.selenium.start()

    def searchReplace(self):
        sel = self.selenium
        sel.open("/eduCommons")
        sel.click("link=Log in")
        sel.type("__ac_name", "admin")
        sel.type("__ac_password", "test1234")
        sel.click("submit")
        sel.click("link=Home")
        self.failUnless(sel.is_text_present("some extra help"))
        sel.click("link=Search/Replace")
        sel.wait_for_page_to_load("30000")
        sel.type("find_what", "help")
        sel.type("replace_with", "HELP!")
        sel.click("form.button.PreviewResults")
        sel.click("form.button.ReplaceAll")
        sel.click("link=Home")
        sel.wait_for_page_to_load("30000")
        self.failUnless(sel.is_text_present("HELP!"))
        sel.click("link=Search/Replace")
        sel.wait_for_page_to_load("30000")
        sel.type("find_what", "HELP!")
        sel.type("replace_with", "help")
        sel.click("match_case")
        sel.click("form.button.PreviewResults")
        self.failUnless(sel.is_text_present("looking for some extra HELP!"))
        sel.click("form.button.ReplaceAll")
        sel.click("link=Home")
        self.failUnless(sel.is_text_present("some extra help"))
    
    def tearDown(self):
        self.selenium.stop()
        self.assertEqual([], self.verificationErrors)

if __name__ == "__main__":
    unittest.main()
