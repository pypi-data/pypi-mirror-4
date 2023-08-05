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
# These are for the smtp server
import smtpd
import asyncore
import threading

smtpServer = smtpd.DebuggingServer(('127.0.0.1', 1025), None)

def smtpLoop():
    asyncore.loop()

class DivisionTests(unittest.TestCase):
    def setUp(self):
        self.verificationErrors = []
        self.selenium = selenium("localhost",port, browser,url,instance)
        self.selenium.start()
        self.smtpserver = Popen(["./fakeSMTPServer.py"],shell=True)
    
    def test_new_email(self):
        sel = self.selenium
        # We login using the wrapped function
        sel.login("admin","test1234")
        # Here the test starts
        sel.click("link=Site Setup")
        sel.wait_for_page_to_load("30000")
        sel.click("link=Mail")
        sel.wait_for_page_to_load("30000")
        sel.type("form.email_from_address", "test@email.com")
        sel.click("form.actions.save")
        sel.wait_for_page_to_load("30000")
        try: self.failUnless(sel.is_text_present("Changes saved."))
        except AssertionError, e: self.verificationErrors.append(str(e))
        sel.click("link=Home")
        sel.wait_for_page_to_load("30000")
        sel.click("//img[@alt='Send this']")
        sel.wait_for_page_to_load("30000")
        sel.type("send_to_address", "reciever@email.com")
        sel.type("send_from_address", "sender@email.com")
        sel.type("comment", "This is a test content.")
        sel.click("form.button.Send")
        sel.wait_for_page_to_load("30000")
        self.failUnless(sel.is_element_present("//dl[contains(@class,\"info\")]/dd[text() = \"Mail sent.\"]"))

    def tearDown(self):
        self.selenium.stop()
        self.assertEqual([], self.verificationErrors)
        print "Killing SMTP Server"
        if (platform.system() == 'Windows'):
                import win32api
                handle = win32api.OpenProcess(1, 0, self.smtpserver.pid)
                win32api.TerminateProcess(handle, 0)
        else:
                os.kill(self.smtpserver.pid,signal.SIGTERM)

if __name__ == "__main__":
    unittest.main()
