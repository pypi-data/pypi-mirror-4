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

from zope.interface import implements
from zope.formlib import form
from plone.portlets.interfaces import IPortletDataProvider
from plone.app.portlets.portlets import base
from enpraxis.educommons import eduCommonsMessageFactory as _
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.component import getUtility, getMultiAdapter
from enpraxis.educommons.utilities.interfaces import IECUtility

class IReuseCoursePortlet(IPortletDataProvider):
    """ A portlet that facilitates course reuse. """


class Assignment(base.Assignment):

    implements(IReuseCoursePortlet)
    title = _(u'Reuse Course')

    
class Renderer(base.Renderer):

    render = ViewPageTemplateFile('reusecourse.pt')

    def __init__(self, context, request, view, manager, data):
        super(Renderer, self).__init__(context, request, view, manager, data)
        portal_state = getMultiAdapter((self.context, self.request), name=u'plone_portal_state')
        self.anonymous = portal_state.anonymous()
        self.ecutil = getUtility(IECUtility)
        self.ecparent = self.ecutil.FindECParent(context)

    @property
    def available(self):
        #Only make visible if Course is Published and IMS Package exists
        #IMS pkg name
        wf_tool = self.ecparent.portal_workflow
        ims_pkg = ''
        ims_pkg = '%s.zip' % self.ecparent.id
        
        if self.ecparent.Type() == 'Course':
            if 'Published' == wf_tool.getInfoFor(self.ecparent, 'review_state') and hasattr(self.ecparent, ims_pkg):
                if 'Published' == wf_tool.getInfoFor(getattr(self.ecparent, ims_pkg), 'review_state'):
                    return True
        return False

    @property
    def ims_id(self):
        return '%s.zip' % self.ecparent.id


class AddForm(base.NullAddForm):

    form_fields = form.Fields(IReuseCoursePortlet)

    def create(self):
        return Assignment()
