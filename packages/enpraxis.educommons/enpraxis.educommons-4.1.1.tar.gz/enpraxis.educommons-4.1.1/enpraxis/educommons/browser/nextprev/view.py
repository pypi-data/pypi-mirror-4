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

from plone.app.layout.viewlets import ViewletBase
from plone.app.layout.nextprevious.interfaces import INextPreviousProvider
from plone.memoize import view, instance

from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile
from Acquisition import aq_inner, aq_parent

from enpraxis.educommons.utilities.interfaces import IECUtility
from zope.component import getUtility

class NextPreviousView(BrowserView):
    """Information about next/previous navigation
    """

    @view.memoize
    def next(self):
        provider = self._provider()
        if provider is None:
           return None
        return provider.getNextItem(aq_inner(self.context))
    
    @view.memoize
    def previous(self):
        provider = self._provider()
        if provider is None:
            return None
        return provider.getPreviousItem(aq_inner(self.context))

    @view.memoize
    def enabled(self):
        provider = self._provider()
        if provider is None:
            return False
        return provider.enabled

    @instance.memoize
    def _provider(self):
        # Note - the next/previous provider is the container of this object!
        # This may not support next/previous navigation, so code defensively
        ecutil = getUtility(IECUtility)
        ecparent = ecutil.FindECParent(self.context)

        if 'Course' == ecparent.Type():
            return INextPreviousProvider(ecparent)
        else:
            return INextPreviousProvider(aq_parent(aq_inner(self.context)), None)

    @view.memoize
    def isViewTemplate(self):
        plone = getMultiAdapter((self.context, self.request), name=u'plone_context_state')
        return plone.is_view_template()


class NextPreviousViewlet(ViewletBase, NextPreviousView):
    render = ZopeTwoPageTemplateFile('nextprevious.pt')


class NextPreviousLinksViewlet(ViewletBase, NextPreviousView):
    render = ZopeTwoPageTemplateFile('links.pt')
