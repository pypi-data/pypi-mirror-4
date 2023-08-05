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
# This number is used for the division title created in this test
random_number = str(random.randint(1111,9999))

class CourseTest(unittest.TestCase):
    def setUp(self):
        self.verificationErrors = []
        self.selenium = selenium("localhost",port, browser,url,instance)
        # The division will be created in this first test and will be used in the rest
        # of the tests. You can change the following name without breaking the test
        self.divisionTitle = "Test Division " + random_number
        self.selenium.start()
    
    def test_course_builder(self):
        # You can change the tile used for the test course
        # just changing the following variable
        courseTitle = "Test Course " + str(random.randint(1111,9999))
        sel = self.selenium
        # We login using the wrapped function
        sel.login("admin","test1234")
        # Here the test starts
        sel.click("link=Build a Course")
        sel.wait_for_page_to_load("30000")
        sel.type("form.division.textfield", self.divisionTitle)
        sel.type("form.coursename", courseTitle)
        sel.type("form.courseid", "1.0")
        sel.type("form.courseterm", "Testing")
        sel.click("form.actions.Submit")
        sel.wait_for_page_to_load("30000")
        sel.type("description", "Test Desc")
        sel.click("form_submit")
        sel.wait_for_page_to_load("30000")
        # Creation Validations
        self.failUnless(sel.is_text_present("Changes saved."))
        try: self.assertEqual("1.0 - " + courseTitle + ", Testing", sel.get_text("parent-fieldname-title"))
        except AssertionError, e: self.verificationErrors.append("Wrong title created")
        # Breadcrumbs validations
        try: self.failUnless(sel.validate_breadcrumbs("Home",self.divisionTitle, courseTitle))
        except AssertionError, e: self.verificationErrors.append("Errors in the breadcrumbs")
        # Check it's created from outside
        sel.click("link=" + self.divisionTitle)
        sel.wait_for_page_to_load("30000")
        try: self.failUnless(sel.validate_breadcrumbs("Home",self.divisionTitle))
        except AssertionError, e: self.verificationErrors.append("Errors in the breadcrumbs")
        try: self.failUnless(sel.is_element_present('//div[@class="division-listing"]//a[contains(text(),"1.0 - '+ courseTitle +', Testing")]'))
        except AssertionError, e: self.verificationErrors.append("Course not found inside the Division")
        sel.click("link=Home")
        sel.wait_for_page_to_load("30000")
        sel.click("link=list of courses")
        sel.wait_for_page_to_load("30000")
        while sel.is_element_present('link=1.0 - '+ courseTitle +', Testing') or sel.is_element_present('//span[@class="next"]/a'):
            if sel.is_element_present('link=1.0 - '+ courseTitle +', Testing'): break
            else: 
                sel.click('//span[@class="next"]/a')
                sel.wait_for_page_to_load("30000")
        else:
            self.verificationErrors.append("Course not found in the courses list")

    def test_new_course_basic(self):
        # You can change the tile used for the test course
        # just changing the following variable
        courseTitle = "Test Course " + str(random.randint(1111,9999))
        sel = self.selenium
        # We login using the wrapped function
        sel.login("admin","test1234")
        # Here the test starts
        sel.click("link=" + self.divisionTitle)
        sel.wait_for_page_to_load("30000")
        # Course creation
        sel.click("//dl[@id='plone-contentmenu-factories']/dt/a")
        sel.click("//a[@id='course']/span")
        sel.wait_for_page_to_load("30000")
        sel.type("title", courseTitle)
        sel.type("description", "This is an example description.")
        sel.type("courseId", "1.0")
        sel.type("term", "Testing")
        sel.type("structure", "Phase 1.\nPhase 2.\nPhase 3.")
        sel.select("level", "label=Graduate")
        sel.type("instructorName", "Instructor Name")
        sel.type("instructorEmail", "instructor@email.com")
        sel.click("displayInstEmail")
        sel.click("instructorAsCreator")
        sel.click("form_submit")
        sel.wait_for_page_to_load("30000")
        # Creation Validations
        self.failUnless(sel.is_text_present("Changes saved."))
        try: self.assertEqual("1.0 - " + courseTitle + ", Testing", sel.get_text("parent-fieldname-title"))
        except AssertionError, e: self.verificationErrors.append("Wrong title created")
        # Breadcrumbs validations
        try: self.failUnless(sel.validate_breadcrumbs("Home",self.divisionTitle, courseTitle))
        except AssertionError, e: self.verificationErrors.append("Errors in the breadcrumbs")
        # Check it's created from outside
        sel.click("link=" + self.divisionTitle)
        sel.wait_for_page_to_load("30000")
        try: self.failUnless(sel.validate_breadcrumbs("Home",self.divisionTitle))
        except AssertionError, e: self.verificationErrors.append("Errors in the breadcrumbs")
        try: self.failUnless(sel.is_element_present('//div[@class="division-listing"]//a[contains(text(),"1.0 - '+ courseTitle +', Testing")]'))
        except AssertionError, e: self.verificationErrors.append("Course not found inside the Division")
        sel.click("link=Home")
        sel.wait_for_page_to_load("30000")
        sel.click("link=list of courses")
        sel.wait_for_page_to_load("30000")
        while sel.is_element_present('link=1.0 - '+ courseTitle +', Testing') or sel.is_element_present('//span[@class="next"]/a'):
            if sel.is_element_present('link=1.0 - '+ courseTitle +', Testing'): break
            else: 
                sel.click('//span[@class="next"]/a')
                sel.wait_for_page_to_load("30000")
        else:
            self.verificationErrors.append("Course not found in the courses list")
    
    def test_new_course_required_fields(self):
        courseTitle = "Test Course " + str(random.randint(1111,9999))
        sel = self.selenium
        # We login using the wrapped function
        sel.login("admin","test1234")
        # Here the test starts
        sel.click("link=" + self.divisionTitle)
        sel.wait_for_page_to_load("30000")
        sel.click("//dl[@id='plone-contentmenu-factories']/dt/a")
        sel.click("//a[@id='course']/span")
        sel.wait_for_page_to_load("30000")
        sel.type("title", "")
        sel.type("description", "This is an example description.")
        sel.type("courseId", "1.0")
        sel.type("term", "Testing")
        sel.type("structure", "Phase 1.\nPhase 2.\nPhase 3.")
        sel.select("level", "label=Graduate")
        sel.type("instructorName", "Instructor Name")
        sel.type("instructorEmail", "instructor@email.com")
        sel.click("displayInstEmail")
        sel.click("instructorAsCreator")
        sel.click("form_submit")
        sel.wait_for_page_to_load("30000")
        # We look for the error message
        self.failUnless(sel.is_element_present('//div[input[@id="title"]]/span[@class="fieldRequired"]'))
        # And try the rest are not required
        sel.type("title", courseTitle)
        sel.type("description", "")
        sel.type("courseId", "")
        sel.type("term", "")
        sel.type("structure", "")
        sel.select("level", "label=Undergraduate")
        sel.type("instructorName", "")
        sel.type("instructorEmail", "")
        sel.click("displayInstEmail")
        sel.click("instructorAsCreator")
        sel.click("form_submit")
        sel.wait_for_page_to_load("30000")
        self.failUnless(sel.is_text_present("Changes saved."))
    
    def test_new_course_unicode(self):
        unicodeString = u"李四 王慎强 ΔΑΙΜΟΝΑΚΟΣ ΓΕΩΡΓΙΟΣ díaçñÑ "
        courseTitle = unicodeString + str(random.randint(1111,9999))
        sel = self.selenium
        # We login using the wrapped function
        sel.login("admin","test1234")
        # Here the test starts
        sel.click("link=" + self.divisionTitle)
        sel.wait_for_page_to_load("30000")
        # Course Creation
        sel.click("//dl[@id='plone-contentmenu-factories']/dt/a")
        sel.click("//a[@id='course']/span")
        sel.wait_for_page_to_load("30000")
        sel.type("title", courseTitle)
        sel.type("description", unicodeString + "desc")
        sel.type("courseId", unicodeString + "id")
        sel.type("term", unicodeString + "term")
        sel.type("structure", unicodeString + "struct")
        sel.select("level", "label=Graduate")
        sel.type("instructorName", unicodeString + "inst")
        sel.type("instructorEmail", unicodeString + "email")
        sel.click("displayInstEmail")
        sel.click("instructorAsCreator")
        sel.click("form_submit")
        sel.wait_for_page_to_load("30000")
        # Creation Validations
        longName = unicodeString + 'id - '+ courseTitle + ', ' + unicodeString + "term"
        self.failUnless(sel.is_text_present("Changes saved."))
        try: self.assertEqual(longName, sel.get_text("parent-fieldname-title"))
        except AssertionError, e: self.verificationErrors.append("Wrong title created")
        try: self.failUnless(sel.validate_breadcrumbs("Home",self.divisionTitle, courseTitle))
        except AssertionError, e: self.verificationErrors.append("Errors in the breadcrumbs")
        # Check it's created from outside
        sel.click("link=" + self.divisionTitle)
        sel.wait_for_page_to_load("30000")
        try: self.failUnless(sel.validate_breadcrumbs("Home",self.divisionTitle))
        except AssertionError, e: self.verificationErrors.append("Errors in the breadcrumbs")
        try: self.failUnless(sel.is_element_present(u'//div[@class="division-listing"]//a[contains(text(), "' + longName + '")]'))
        except AssertionError, e: self.verificationErrors.append("Course not found inside the Division")
        sel.click("link=Home")
        sel.wait_for_page_to_load("30000")
        sel.click("link=list of courses")
        sel.wait_for_page_to_load("30000")
        while sel.is_element_present('link='+longName) or sel.is_element_present('//span[@class="next"]/a'):
            if sel.is_element_present('link='+ longName): break
            else: 
                sel.click('//span[@class="next"]/a')
                sel.wait_for_page_to_load("30000")
        else:
            self.verificationErrors.append("Course not found in the courses list")

    def tearDown(self):
        self.selenium.stop()
        self.assertEqual([], self.verificationErrors)

if __name__ == "__main__":
    unittest.main()
