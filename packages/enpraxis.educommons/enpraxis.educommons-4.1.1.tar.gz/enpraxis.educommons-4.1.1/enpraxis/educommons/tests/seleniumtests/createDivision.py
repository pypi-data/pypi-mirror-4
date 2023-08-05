# -*- coding: iso-8859-15 -*-
##################################################################################
#    Copyright (c) 2009 Massachusetts Institute of Technology, All rights reserved.
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

__author__  = '''Santiago Suarez Ordoñez'''
__version__   = '$ Revision 0.0 $'[11:-2]
# -*- coding: iso-8859-15 -*-

from seleniumWrapper import selenium
import unittest
import random

class DivisionTests(unittest.TestCase):
    def setUp(self):
        self.verificationErrors = []
        self.selenium = selenium("localhost",port, browser,url,instance)
        self.selenium.start()
    
    def test_new_division_basic(self):
        # You can change the tile used for the test division
        # just changing the following variable
        divisionTitle = "Test Division " + str(random.randint(1111,9999))
        sel = self.selenium
        # We login using the wrapped function
        sel.login("admin","test1234")
        # Here the test starts
        # Division creation
        sel.click("//dl[@id='plone-contentmenu-factories']/dt/a/span[1]")
        sel.click("//a[@id='division']/span")
        sel.wait_for_page_to_load("30000")
        sel.type("title", divisionTitle)
        sel.type("description", "This is a test division.")
        sel.click("form_submit")
        sel.wait_for_page_to_load("30000")
        # Creation Validation
        self.failUnless(sel.is_text_present("Changes saved."))
        try: self.failUnless(sel.is_element_present('//dl[dt[span[text()="Departments"]]]/dd[a[contains(text(),"' + divisionTitle + '")]]'))
        except AssertionError, e: self.verificationErrors.append("Division missing under departments portlet")
        try: self.assertEqual(divisionTitle, sel.get_text("parent-fieldname-title"))
        except AssertionError, e: self.verificationErrors.append("Wrong division title")
        try: self.failUnless(sel.validate_breadcrumbs("Home",divisionTitle))
        except AssertionError, e: self.verificationErrors.append("Errors in the breadcrumbs")
        # Some checks from outside
        sel.click("link=Home")
        sel.wait_for_page_to_load("30000")
        try: self.failUnless(sel.is_element_present('//dl[dt[span[text()="Departments"]]]/dd[a[contains(text(),"' + divisionTitle + '")]]'))
        except AssertionError, e: self.verificationErrors.append("Division missing under departments portlet in Home")

    def test_new_division_required_fields(self):
        # You can change the tile used for the test division
        # just changing the following variable
        divisionTitle = "Test Division " + str(random.randint(1111,9999))
        sel = self.selenium
        # We login using the wrapped function
        sel.login("admin","test1234")
        # Here the test starts
        # Division creation
        sel.click("//dl[@id='plone-contentmenu-factories']/dt/a/span[1]")
        sel.click("//a[@id='division']/span")
        sel.wait_for_page_to_load("30000")
        sel.type("title", "")
        sel.click("form_submit")
        sel.wait_for_page_to_load("30000")
        self.failUnless(sel.is_element_present('//div[input[@id="title"]]/span[@class="fieldRequired"]'))
        sel.type("title", divisionTitle)
        sel.type("description", "")
        sel.click("form_submit")
        sel.wait_for_page_to_load("30000")
        self.failUnless(sel.is_text_present("Changes saved."))
    
    def test_new_division_unicode(self):
        unicodeString = u"李四 王慎强 ΔΑΙΜΟΝΑΚΟΣ ΓΕΩΡΓΙΟΣ díaçñÑ"
        divisionTitle = unicodeString + str(random.randint(1111,9999))
        description = unicodeString + "desc"
        sel = self.selenium
        # We login using the wrapped function
        sel.login("admin","test1234")
        # Here we add a Division
        sel.click("//dl[@id='plone-contentmenu-factories']/dt/a/span[1]")
        sel.click("//a[@id='division']/span")
        sel.wait_for_page_to_load("30000")
        sel.type("title", divisionTitle)
        sel.type("description", description)
        sel.click("form_submit")
        sel.wait_for_page_to_load("30000")
        self.failUnless(sel.is_text_present("Changes saved."))
        try: self.failUnless(sel.is_element_present('//dl[dt[span[text()="Departments"]]]/dd[a[contains(text(),"' + divisionTitle + '")]]'))
        except AssertionError, e: self.verificationErrors.append("Division missing under departments portlet")
        try: self.assertEqual(divisionTitle, sel.get_text("parent-fieldname-title"))
        except AssertionError, e: self.verificationErrors.append("Wrong division title")
        try: self.failUnless(sel.validate_breadcrumbs("Home",divisionTitle))
        except AssertionError, e: self.verificationErrors.append("Errors in the breadcrumbs")
        # Some checks from outside
        sel.click("link=Home")
        sel.wait_for_page_to_load("30000")
        try: self.failUnless(sel.is_element_present('//dl[dt[span[text()="Departments"]]]/dd[a[contains(text(),"' + divisionTitle + '")]]'))
        except AssertionError, e: self.verificationErrors.append("Division missing under departments portlet in Home")

    def tearDown(self):
        self.selenium.stop()
        self.assertEqual([], self.verificationErrors)

if __name__ == "__main__":
    unittest.main()
