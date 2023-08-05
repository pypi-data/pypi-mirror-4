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
import os, sys
import unittest
import random

class CourseTest(unittest.TestCase):
    def setUp(self):
        self.verificationErrors = []
        self.selenium = selenium("localhost",port, browser,url,instance)
        # The division will be created in this first test and will be used in the rest
        # of the tests. You can change the following name without breaking the test
        self.selenium.start()
    
    def test_ims_upload_basic(self):
        # You can change the tile used for the test course
        # just changing the following variable
        courseTitle = "Intro to 1's and 0's"
        divisionTitle = "Test Division " + str(random.randint(1111,9999))
        sel = self.selenium
        # We login using the wrapped function
        sel.login("admin","test1234")
        # We start creating the course by uploading the ims
        sel.click("link=Build a Course")
        sel.wait_for_page_to_load("30000")
        sel.type("form.division.textfield", divisionTitle)
        sel.type("form.coursename", courseTitle)
        sel.type("form.filename", os.path.join(os.path.dirname(__file__),"ims-intro-to-1s-and-0s.zip"))
        sel.click("form.actions.Submit")
        sel.wait_for_page_to_load("30000")
        # And start validating the first result of the upload
        self.assertEqual("Add Course", sel.get_text("css=h1.documentFirstHeading"))
        try: 
            self.assertEqual("Intro to 1's and 0's", sel.get_value("title"))
            self.assertEqual("INST 101", sel.get_value("courseId"))
            self.assertEqual("Fall 2007", sel.get_value("term"))
            self.assertEqual("Mr. Web", sel.get_value("instructorName"))
            self.assertEqual("testing@mail.com", sel.get_value("instructorEmail"))
            self.failUnless(sel.is_checked("displayInstEmail"))
        except AssertionError, e: self.verificationErrors.append("Wrong data taken from the IMS")
        # Saving the Course
        sel.click("form_submit")
        sel.wait_for_page_to_load("30000")
        self.failUnless(sel.is_text_present("Changes saved."))
        # Breadcrumbs validations
        try: self.failUnless(sel.validate_breadcrumbs("Home",divisionTitle, u"Intro to 1's and 0's"))
        except AssertionError, e: self.verificationErrors.append("Errors in the breadcrumbs")
        # Course created validations
        try: self.failUnless(sel.is_text_present("INST 101 - Intro to 1's and 0's, Fall 2007"))
        except AssertionError, e: self.verificationErrors.append("Wrong title created")
        try:
            self.assertEqual(sel.get_text('//td[@id="aboutInfo"]/h3'),u"Intro to 1's and 0's")
            self.assertTrue("Mr. Web, Ph.D." in sel.get_text('//td[@id="aboutInfo"]'))
            self.assertEqual(sel.get_text('//div[@id="about"]/h4'),u"Course Description")
            self.assertTrue("This is the course's description." in sel.get_text('//div[@id="about"]'))
        except AssertionError, e: self.verificationErrors.append("Error in the HTML intro")
        # Syllabus
        sel.click("link=Syllabus")
        sel.wait_for_page_to_load("30000")
        try: self.assertEqual("Syllabus", sel.get_text("css=h1.documentFirstHeading"))
        except AssertionError, e: self.verificationErrors.append("Error on Syllabus page title")
        try: self.failUnless(sel.validate_breadcrumbs("Home",divisionTitle,courseTitle,"Syllabus"))
        except AssertionError, e: self.verificationErrors.append("Errors in the breadcrumbs")
        try:
            self.assertEqual(sel.get_text('document.getElementsByTagName("h2")[0]'),
                    'Course Description')
            self.assertEqual(sel.get_text('document.getElementsByTagName("h2")[1]'),
                    'Course Objectives')
            self.assertEqual(sel.get_text('document.getElementsByTagName("h2")[2]'),
                    'Prerequisites')
            self.assertEqual(sel.get_text('document.getElementsByTagName("h2")[3]'),
                    'Required Textbook')
            self.assertEqual(sel.get_text('document.getElementsByTagName("h2")[4]'),
                    'Other Reading')
            self.assertEqual(sel.get_text('document.getElementsByTagName("h2")[5]'),
                    'Grading')
        except AssertionError, e: self.verificationErrors.append("Error on Syllabus page")
        # Course Schedule
        sel.click("link=Course Schedule")
        sel.wait_for_page_to_load("30000")
        try: self.assertEqual("Course Schedule", sel.get_text("css=h1.documentFirstHeading"))
        except AssertionError, e: self.verificationErrors.append("Error on Course Schedulle page title")
        try: self.failUnless(sel.validate_breadcrumbs("Home",divisionTitle,courseTitle,"Course Schedule"))
        except AssertionError, e: self.verificationErrors.append("Errors in the breadcrumbs")
        try:
            self.assertEqual(sel.get_text('document.getElementsByTagName("h2")[0]'),
                    'Course Schedule Information')
        except AssertionError, e: self.verificationErrors.append("Error on Course Schedule page")
        # About Professor
        sel.click("link=About Professor")
        sel.wait_for_page_to_load("30000")
        try: self.assertEqual("About Professor", sel.get_text("css=h1.documentFirstHeading"))
        except AssertionError, e: self.verificationErrors.append("Error on About Professor page title")
        try: self.failUnless(sel.validate_breadcrumbs("Home",divisionTitle,courseTitle,"About Professor"))
        except AssertionError, e: self.verificationErrors.append("Errors in the breadcrumbs")
        try:
            self.assertEqual(sel.get_text('document.getElementsByTagName("h3")[0]'),
                    'Professor X, Ph.D.')
        except AssertionError, e: self.verificationErrors.append("Error on About Professor page")
        sel.click("link=Home")
        sel.wait_for_page_to_load("30000")


#        # Check it's created from outside
#        sel.click("link=" + self.divisionTitle)
#        sel.wait_for_page_to_load("30000")
#        try: self.failUnless(sel.validate_breadcrumbs("Home",self.divisionTitle))
#        except AssertionError, e: self.verificationErrors.append("Errors in the breadcrumbs")
#        try: self.failUnless(sel.is_element_present('//div[@class="division-listing"]//a[contains(text(),"1.0 - '+ courseTitle +', Testing")]'))
#        except AssertionError, e: self.verificationErrors.append("Course not found inside the Division")
#        sel.click("link=Home")
#        sel.wait_for_page_to_load("30000")
#        sel.click("link=list of courses")
#        sel.wait_for_page_to_load("30000")
#        while sel.is_element_present('link=1.0 - '+ courseTitle +', Testing') or sel.is_element_present('//span[@class="next"]/a'):
#            if sel.is_element_present('link=1.0 - '+ courseTitle +', Testing'): break
#            else: 
#                sel.click('//span[@class="next"]/a')
#                sel.wait_for_page_to_load("30000")
#        else:
#            self.verificationErrors.append("Course not found in the courses list")


    def tearDown(self):
        self.selenium.stop()
        self.assertEqual([], self.verificationErrors)
