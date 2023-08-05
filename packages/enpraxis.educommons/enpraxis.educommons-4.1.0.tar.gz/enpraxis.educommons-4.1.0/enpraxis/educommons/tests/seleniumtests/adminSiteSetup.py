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

#checks administraitors capabilitis in site setup

from seleniumWrapper import selenium
import unittest, time, re
import unittest
import random
import time

class NewTest(unittest.TestCase):
    def setUp(self):
        self.verificationErrors = []
        self.selenium = selenium("localhost",port, browser,url,instance)
        self.selenium.start()
    
    def test_new(self):
        sel = self.selenium
        sel.open("/eduCommons/logged_out")
        sel.type("__ac_name", "admin")
        sel.type("__ac_password", "test1234")
        sel.click("submit")
	sel.wait_for_page_to_load("30000")
        sel.click("link=Site Setup")
	sel.wait_for_page_to_load("30000")
        try: self.failUnless(sel.is_text_present("Visual editor"))
        except AssertionError, e: self.verificationErrors.append(str(e))
        try: self.failUnless(sel.is_text_present("Add-on Products"))
        except AssertionError, e: self.verificationErrors.append(str(e))
        try: self.failUnless(sel.is_text_present("Errors"))
        except AssertionError, e: self.verificationErrors.append(str(e))
        try: self.failUnless(sel.is_text_present("Search"))
        except AssertionError, e: self.verificationErrors.append(str(e))
        try: self.failUnless(sel.is_text_present("Left Skin CSS Settings"))
	except AssertionError, e: self.verificationErrors.append(str(e))
        try: self.failUnless(sel.is_text_present("Mail"))
	except AssertionError, e: self.verificationErrors.append(str(e))
        try: self.failUnless(sel.is_text_present("Site"))
        except AssertionError, e: self.verificationErrors.append(str(e))
        try: self.failUnless(sel.is_text_present("Zope Management Interface"))
        except AssertionError, e: self.verificationErrors.append(str(e)) 


    def tearDown(self):
        self.selenium.stop()
        self.assertEqual([], self.verificationErrors)

if __name__ == "__main__":
    unittest.main()
