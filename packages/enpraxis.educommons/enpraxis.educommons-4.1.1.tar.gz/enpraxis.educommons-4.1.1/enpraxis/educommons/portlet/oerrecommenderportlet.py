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


class IOerRecommenderPortlet(IPortletDataProvider):
    """ A OER Recommender Portlet. """

class Assignment(base.Assignment):
    """Assignment for OER Recommender Portlet """

    implements(IOerRecommenderPortlet)

    title = _(u'OER Recommender Portlet')


class Renderer(base.Renderer):
    """ Render the OER Portlet """
    render = ViewPageTemplateFile('oerrecommender.pt')


    def __init__(self, context, request, view, manager, data):
        super(Renderer, self).__init__(context, request, view, manager, data)
        self.props = self.context.portal_properties.educommons_properties

    @property
    def available(self):
        return self.props.oerrecommender_enabled



class AddForm(base.NullAddForm):
    form_fields = form.Fields(IOerRecommenderPortlet)
    
    def create(self):
        return Assignment()


