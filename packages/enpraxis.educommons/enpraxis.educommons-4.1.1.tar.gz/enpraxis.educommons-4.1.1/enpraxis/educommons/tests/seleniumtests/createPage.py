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
import time
# This number is used for the division and course title created in this test
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
        # Creation Validations
        self.failUnless(sel.is_text_present("Changes saved."))
        try: self.assertEqual("1.0 - " + self.courseTitle + ", Testing", sel.get_text("parent-fieldname-title"))
        except AssertionError, e: self.verificationErrors.append("Wrong title created")
        # Breadcrumbs validations
        try: self.failUnless(sel.validate_breadcrumbs("Home",self.divisionTitle, self.courseTitle))
        except AssertionError, e: self.verificationErrors.append("Errors in the breadcrumbs")

    def test_new_page_basic(self):
        pageTitle = "Test Page " + str(random.randint(1111,9999))
        sel = self.selenium
        # We login using the wrapped function
        sel.login("admin","test1234")
        # Here the test starts
        sel.click("link=" + self.divisionTitle)
        sel.wait_for_page_to_load("30000")
        sel.click("link=1.0 - " + self.courseTitle + ", Testing")
        sel.wait_for_page_to_load("30000")
        sel.click('//span[contains(text(),"Add new")]')
        sel.click('//span[@class="subMenuTitle" and text() = "Page"]')
        sel.wait_for_page_to_load("30000")
        sel.type("title", pageTitle)
        sel.type("description", "Test Description")
        sel.click("kupu-source-button")
        sel.type("text", "<p>This is example content, you should be able to write in html and paste <a href=#>links</a></p>")
        sel.click("form_submit")
        sel.wait_for_page_to_load("30000")
        # Creation Validations
        self.failUnless(sel.is_text_present("Changes saved."))
        try: self.assertEqual(pageTitle, sel.get_text("parent-fieldname-title"))
        except AssertionError, e: self.verificationErrors.append("Wrong title created")
        try: self.failUnless(sel.is_text_present("This is example content, you should be able to write in html and paste links"))
        except AssertionError, e: self.verificationErrors.append("Content is not present")
        try: self.failUnless(sel.is_element_present("link=links"))
        except AssertionError, e: self.verificationErrors.append("Link on Page's content is not present")
        try: self.failUnless(sel.validate_breadcrumbs("Home",self.divisionTitle, self.courseTitle, pageTitle))
        except AssertionError, e: self.verificationErrors.append("Errors in the breadcrumbs")
        sel.click("link=" + self.courseTitle)
        sel.wait_for_page_to_load("30000")
        sel.click("link=Contents")
        for i in range(60):
            try:
                if sel.is_element_present("//table[@summary=\"Content listing\"]"): break
            except: pass
            time.sleep(1)
        else: self.fail("time out")
        try: self.failUnless(sel.is_element_present("link=" + pageTitle))
        except AssertionError, e: self.verificationErrors.append("Page not found from outside")

    def test_new_page_required_fields(self):
        pageTitle = "Test Page " + str(random.randint(1111,9999))
        sel = self.selenium
        # We login using the wrapped function
        sel.login("admin","test1234")
        # Here the test starts
        sel.click("link=" + self.divisionTitle)
        sel.wait_for_page_to_load("30000")
        sel.click("link=1.0 - " + self.courseTitle + ", Testing")
        sel.wait_for_page_to_load("30000")
        sel.click('//span[contains(text(),"Add new")]')
        sel.click('//span[@class="subMenuTitle" and text() = "Page"]')
        sel.wait_for_page_to_load("30000")
        sel.type("description", "Test Description")
        sel.click("kupu-source-button")
        sel.type("text", "<p>This is example content, you should be able to write in html and paste <a href=#>links</a></p>")
        sel.click("form_submit")
        sel.wait_for_page_to_load("30000")
        # We look for the error message
        self.failUnless(sel.is_element_present('//div[input[@id="title"]]/span[@class="fieldRequired"]'))
        # And try the rest are not required
        sel.type("title", pageTitle)
        sel.click("form_submit")
        sel.wait_for_page_to_load("30000")
        self.failUnless(sel.is_text_present("Changes saved."))

    def test_new_page_unicode(self):
        unicodeString = u"李四 王慎强 ΔΑΙΜΟΝΑΚΟΣ ΓΕΩΡΓΙΟΣ díaçñÑ"
        pageTitle = unicodeString + str(random.randint(1111,9999))
        sel = self.selenium
        # We login using the wrapped function
        sel.login("admin","test1234")
        # Here the test starts
        sel.click("link=" + self.divisionTitle)
        sel.wait_for_page_to_load("30000")
        # Page Creation
        sel.click("link=1.0 - " + self.courseTitle + ", Testing")
        sel.wait_for_page_to_load("30000")
        sel.click('//span[contains(text(),"Add new")]')
        sel.click('//span[@class="subMenuTitle" and text() = "Page"]')
        sel.wait_for_page_to_load("30000")
        sel.type("title", pageTitle)
        sel.type("description", unicodeString + " Test Description")
        sel.click("kupu-source-button")
        sel.type("text", "<p> " + unicodeString + " text </p>")
        # import pdb;pdb.set_trace()
        sel.click("form_submit")
        sel.wait_for_page_to_load("30000")
        # Creation Validations
        self.failUnless(sel.is_text_present("Changes saved."))
        try: self.assertEqual(pageTitle, sel.get_text("parent-fieldname-title"))
        except AssertionError, e: self.verificationErrors.append("Wrong title created")
        try: self.assertEqual(unicodeString+" text", sel.get_text("parent-fieldname-text"))
        except AssertionError, e: self.verificationErrors.append("Wrong Content created. Note: This is a known kupu transform bug.")
        try: self.failUnless(sel.validate_breadcrumbs("Home",self.divisionTitle, self.courseTitle, pageTitle))
        except AssertionError, e: self.verificationErrors.append("Errors in the breadcrumbs")
        sel.click("link=" + self.courseTitle)
        sel.wait_for_page_to_load("30000")
        sel.click("link=Contents")
        for i in range(60):
            try:
                if sel.is_element_present("//table[@summary=\"Content listing\"]"): break
            except: pass
            time.sleep(1)
        else: self.fail("time out")
        try: self.failUnless(sel.is_element_present("link=" + pageTitle))
        except AssertionError, e: self.verificationErrors.append("Page not found from outside")

    def tearDown(self):
        self.selenium.stop()
        self.assertEqual([], self.verificationErrors)
