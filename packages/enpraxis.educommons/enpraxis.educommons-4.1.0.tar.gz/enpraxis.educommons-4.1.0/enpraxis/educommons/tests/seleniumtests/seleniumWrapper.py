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

## coding = utf-8 ##

from selenium import selenium as baseSelenium

class selenium(baseSelenium):
	"""eduCommons Selenium wrapper
	
	This wrapper allows us to factorize code
	by adding additional methods to selenium
	like login (which will actually login a user
	to the eduCommons site) or even the __init__
	itself
	
	Usage: To instantiate the selenium test browser
	just use:
	>>> test = educommonsSelenium()
	
	Note, the environment info (like port, browser and url)
	will be retrieved from the seleniumrunner used to run
	the tests.
	"""

	def __init__(self, host, port, browserStartCommand, browserURL, instance):
		self.host = host
		self.port = port
		self.browserStartCommand = browserStartCommand
		self.browserURL = browserURL
		self.instance = instance
		self.sessionId = None
		self.extensionJs = ""

	def login(self, username, password):
		"""Login a user to the eduCommons site
		
		This function recieves the username and
		password and logs the user to the educommons site.
		
		selenium.login(username,password)"""
		
		self.open(self.instance+"/logged_out")
		self.type("__ac_name", username)
		self.type("__ac_password", password)
		self.click("submit")
		self.wait_for_page_to_load("30000")
		if not self.is_text_present("You are now logged in"):
			raise RuntimeError, "Login problems, please check username and password are correct"
		self.click("link=Home")
		self.wait_for_page_to_load("30000")
		if not self.is_text_present("Welcome to eduCommons"):
			raise RuntimeError, "Login problems, home page could no be reached"

	def validate_breadcrumbs(self, *args):
		"""Validates if the breadcrumbs are correct
		
		This function recieves a list of arguments in the order they should be
		on the breadcrumbs from left to right.
		The last string should be the actual page (which wont be a link).
		
		selenium.validate_breadcrumbs("first page","second page", (...), "final page")"""

		for page in args[:-1]:
			if not self.is_element_present('//div[@id="portal-breadcrumbs"]//a[text()="'
					+ page + '"]'):
				return False
		# Checking the last page (it's not a link)
		if not self.is_element_present('//div[@id="portal-breadcrumbs"]//span[text()="'
				+ args[-1] + '"]'):
			return False
		return True
