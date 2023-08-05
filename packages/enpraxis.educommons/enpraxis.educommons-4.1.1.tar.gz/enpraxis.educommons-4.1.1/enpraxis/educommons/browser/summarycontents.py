##################################################################################
#    Copyright (c) 2004-2009 Utah State University, All rights reserved. 
#    Portions copyright 2009 Massachusetts Institute of Technology, All rights reserved.
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

__author__  = '''Brent Lambert, David Ray, Jon Thomas'''
__version__   = '$ Revision 0.0 $'[11:-2]

from zope.component import getMultiAdapter
from Products.CMFCore.utils import getToolByName
from plone.app.content.browser.foldercontents import FolderContentsView, FolderContentsTable
import urllib
from zope.component import getUtility
from enpraxis.educommons.utilities.interfaces import IECUtility
from plone.app.content.browser.tableview import Table
from kss.core import KSSView
from zope.app.pagetemplate import ViewPageTemplateFile
from Acquisition import aq_parent, aq_inner
from zope.annotation import IAnnotations


class SummaryContentsView(FolderContentsView):
    """
    Override contents table to use FindECParent and use SummaryContentsTable
    """

    def contents_table(self):
	ecutil = getUtility(IECUtility)
	parent = ecutil.FindECParent(self.context)
        path = '/'.join(parent.getPhysicalPath())
        request = self.request
        if request.has_key('state'):
            review_state = request['state']
	else:
	    review_state = ''
        table = SummaryContentsTable(parent, self.request, contentFilter={'path':path,'review_state':review_state})
        return table.render()


class SummaryContentsTable(FolderContentsTable):
    """   
    The foldercontents table renders the table and its actions.
    """                

    def __init__(self, context, request, contentFilter=None):
        """
        Initialize the table
        """
        super(SummaryContentsTable, self).__init__(context, request, contentFilter)

        url = self.context.absolute_url()
        view_url = url + '/summary_contents'
        self.table = SummaryTable(request, url, view_url, self.items,
                           show_sort_column=self.show_sort_column,
                           buttons=self.buttons)

            
    @property
    def buttons(self):
        buttons = []
        portal_actions = getToolByName(self.context, 'portal_actions')
        button_actions = portal_actions.listActionInfos(object=aq_inner(self.context), categories=('folder_buttons', ))

        # Do not show buttons if there is no data, unless there is data to be
        # pasted
        if not len(self.items):
            return []

        for button in button_actions:
            # Make proper classes for our buttons
            if button['id'] not in ['paste','cut','copy','import']:
                buttons.append(self.setbuttonclass(button))
        return buttons

class SummaryTable(Table):
    """
    The table renders a table that is 

    the summary portlet.

    """    

    render = ViewPageTemplateFile("summary_table.pt")
    batching = ViewPageTemplateFile("summary_batching.pt")

class SummaryContentsKSSView(KSSView):
    def update_table(self, pagenumber='1', sort_on='getObjPositionInCourse'):
        self.request.set('sort_on', sort_on)
        self.request.set('pagenumber', pagenumber)
        table = SummaryContentsTable(self.context, self.request,
                                    contentFilter={'sort_on':sort_on})
        return self.replace_table(table)
