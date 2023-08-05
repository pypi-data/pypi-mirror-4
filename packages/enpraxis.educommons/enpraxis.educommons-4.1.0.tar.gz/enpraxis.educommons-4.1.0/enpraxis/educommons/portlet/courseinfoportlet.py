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
from Products.CMFCore.utils import getToolByName

class ICourseInfoPortlet(IPortletDataProvider):
    """ A portlet that contains course information. """


class Assignment(base.Assignment):

    implements(ICourseInfoPortlet)
    title = _(u'Course Info Portlet')

    
class Renderer(base.Renderer):

    render = ViewPageTemplateFile('courseinfo.pt')

    def __init__(self, context, request, view, manager, data):
        super(Renderer, self).__init__(context, request, view, manager, data)
        portal_state = getMultiAdapter((self.context, self.request), name=u'plone_portal_state')
        self.anonymous = portal_state.anonymous()
        self.ecutil = getUtility(IECUtility)
        self.ecparent = self.ecutil.FindECParent(context)
        self.stateCounts = {}
        self.mtool = self.context.portal_membership
        t = 0
        for x in self.contentStates:
            self.stateCounts[x] = self.getStateCount(x)
            t += self.stateCounts[x]
        self.total = t


    @property
    def available(self):
        return self.mtool.checkPermission('Modify portal content', self.context) and not self.context.isTemporary()

    def getStateCount(self, state=''):
        """ Grab states for each object based on a filter """
        contentfilter = {'path':{'query':'/'.join(self.ecparent.getPhysicalPath()),},
                         'review_state':state,}
        brains = self.context.portal_catalog.queryCatalog(contentfilter)

        if brains:
            return len(brains)
        else:
            return 0

    def stateCount(self, state):
        return self.stateCounts[state]
        
    def statePercent(self, state=''):
        if 0 == self.total:
            return '0%'
        else:
            width = float(self.stateCounts[state])/float(self.total) * 100.0
            return '%d%%' %int(width)

    @property
    def contentStates(self):
        return self.context.portal_properties.educommons_properties.workflow_order

class AddForm(base.NullAddForm):

    form_fields = form.Fields(ICourseInfoPortlet)

    def create(self):
        return Assignment()
