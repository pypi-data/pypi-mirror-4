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
class setupSite(unittest.TestCase):
    def setUp(self):
        self.verificationErrors = []
        self.selenium = selenium("localhost",port, browser,url,instance)
        self.selenium.start()

    def createInstance(self):
        sel = self.selenium
        sel.open("/manage")
        sel.select_frame("manage_main")
        sel.select(":action", "label=Plone Site")
        sel.wait_for_page_to_load("30000")
        sel.type("siteid", "eduCommons")
        sel.add_selection("extension_ids", "label=PloneBookmarklets")
        sel.add_selection("extension_ids", "label=ContentLicensing")
        sel.add_selection("extension_ids", "label=IMSTransport")
        sel.add_selection("extension_ids", "label=OpenSearch")
        sel.add_selection("extension_ids", "label=OAI Intercom")
        sel.add_selection("extension_ids", "label=SearchAndReplace")
        sel.add_selection("extension_ids", "label=Zip File Transport")
        sel.add_selection("extension_ids", "label=Left Skin")
        sel.add_selection("extension_ids", "label=Static Site")
        sel.add_selection("extension_ids", "label=eduCommons")
        sel.add_selection("extension_ids", "label=wordpressexchange")
        sel.add_selection("extension_ids", "label=iw.fss (FileSystemStorage)")
        sel.add_selection("extension_ids", "label=Workflow Policy Support (CMFPlacefulWorkflow)")
        sel.add_selection("extension_ids", "label=Working Copy Support (Iterate)")
        sel.add_selection("extension_ids", "label=CacheSetup")
        sel.add_selection("extension_ids", "label=LinguaPlone")
        sel.click("submit")
        sel.wait_for_page_to_load("30000")
    
    def tearDown(self):
        self.selenium.stop()
        self.assertEqual([], self.verificationErrors)

if __name__ == "__main__":
    unittest.main()
