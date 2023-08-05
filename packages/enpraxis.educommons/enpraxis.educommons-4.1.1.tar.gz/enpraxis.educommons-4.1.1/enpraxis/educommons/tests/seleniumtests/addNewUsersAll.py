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

# adds new users

from seleniumWrapper import selenium
import unittest, time, re
import unittest
import random
import time
class AddUsersTest(unittest.TestCase):
    def setUp(self):
        self.verificationErrors = []
        self.selenium = selenium("localhost",port, browser,url,instance)
        self.selenium.start()
    
    def createUsers(self):
        sel = self.selenium
        sel.open("/eduCommons/logged_out")
        sel.type("__ac_name", "admin")
        sel.type("__ac_password", "test1234")
        sel.click("submit")
	sel.wait_for_page_to_load("30000")
        sel.click("link=Site Setup")
        sel.wait_for_page_to_load("30000")
        sel.click("link=Users and Groups")
        sel.wait_for_page_to_load("30000")
        sel.click("form.button.FindAll")
        sel.wait_for_page_to_load("30000")
        sel.click("form.button.AddUser")
        sel.wait_for_page_to_load("30000")
        sel.type("fullname", "john doe")
        sel.type("username", "admin")
        sel.type("email", "test@test.com")
        sel.type("password", "admin")
        sel.type("password_confirm", "admin")
        time.sleep(20)
        sel.click("form.button.Register")
        sel.wait_for_page_to_load("30000")
        sel.open("/eduCommons")
        sel.click("link=Site Setup")
        sel.wait_for_page_to_load("30000")
        sel.click("link=Users and Groups")
        sel.wait_for_page_to_load("30000")
        sel.click("form.button.FindAll")
        sel.wait_for_page_to_load("30000")
        sel.click("form.button.AddUser")
        sel.wait_for_page_to_load("30000")
        sel.type("fullname", "john doe")
        sel.type("username", "producer")
        sel.type("email", "test@test.com")
        sel.type("password", "producer")
        sel.type("password_confirm", "producer")
        time.sleep(20)
        sel.click("form.button.Register")
        import pdb;pdb.set_trace()
        sel.click("form.button.FindAll")
        sel.wait_for_page_to_load("30000")
        sel.open("/eduCommons")
        sel.click("link=Site Setup")
        sel.wait_for_page_to_load("30000")
        sel.click("link=Users and Groups")
        sel.wait_for_page_to_load("30000")
        sel.click("form.button.FindAll")
        sel.wait_for_page_to_load("30000")
        sel.click("form.button.AddUser")
        sel.wait_for_page_to_load("30000")
        sel.type("fullname", "john doe")
        sel.type("username", "quality")
        sel.type("email", "test@test.com")
        sel.type("password", "asdfasdf")
        sel.type("password_confirm", "asdfasdf")
        time.sleep(20)
        sel.click("form.button.Register")
        sel.wait_for_page_to_load("30000")
        sel.click("form.button.FindAll")
        sel.wait_for_page_to_load("30000")
        sel.open("/eduCommons")
        sel.click("link=Site Setup")
        sel.wait_for_page_to_load("30000")
        sel.click("link=Users and Groups")
        sel.wait_for_page_to_load("30000")
        sel.click("form.button.FindAll")
        sel.wait_for_page_to_load("30000")
        sel.click("form.button.AddUser")
        sel.wait_for_page_to_load("30000")
        sel.type("fullname", "john doe")
        sel.type("username", "publisher")
        sel.type("email", "test@test.com")
        sel.type("password", "publisher")
        sel.type("password_confirm", "publisher")
        time.sleep(20)
        sel.click("form.button.Register")
        sel.wait_for_page_to_load("30000")
        sel.click("form.button.FindAll")
        sel.wait_for_page_to_load("30000")
        sel.open("/eduCommons")
        sel.click("link=Site Setup")
        sel.wait_for_page_to_load("30000")
        sel.click("link=Users and Groups")
        sel.wait_for_page_to_load("30000")
        sel.click("form.button.FindAll")
        sel.wait_for_page_to_load("30000")
        sel.click("form.button.AddUser")
        sel.wait_for_page_to_load("30000")
        sel.type("fullname", "john doe")
        sel.type("username", "viewer")
        sel.type("email", "test@test.com")
        sel.type("password", "viewer")
        sel.type("password_confirm", "viewer")
        time.sleep(20)
        sel.click("form.button.Register")
        sel.wait_for_page_to_load("30000")
        sel.click("form.button.FindAll")
        sel.wait_for_page_to_load("30000")
    
    def tearDown(self):
        self.selenium.stop()
        self.assertEqual([], self.verificationErrors)

if __name__ == "__main__":
    unittest.main()
