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


from zope.interface import implements, Interface
from zope.component import adapts
from Products.Five.formlib.formbase import PageForm
from zope.formlib.form import Fields, FormFields, action
from zope.schema import TextLine
from plone.app.portlets.portlets import base
from plone.portlets.interfaces import IPortletDataProvider
from enpraxis.educommons import eduCommonsMessageFactory as _
#from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile


class ICourseBuilderPortlet(IPortletDataProvider):
    """ A course building portlet """


class Assignment(base.Assignment):
    """ Assignment """

    implements(ICourseBuilderPortlet)

    title = _(u'Course Builder Portlet')


class Renderer(base.Renderer):
    """ Renderer """

    render = ViewPageTemplateFile('coursebuilder.pt')

#    def __init__(self, context, request, view, manager, data):
#        import pdb; pdb.set_trace()
#        super(base.Renderer, self).__init__(context, request, view, manager, data)
#        self.context = context
#        self.request = request

    @property
    def available(self):
        roles = self.context.portal_membership.getAuthenticatedMember().getRoles()
        if 'Contributor' in roles or 'Producer' in roles or 'Administrator' in roles or 'Manager' in roles:
            return True
        return False

    def hasSchoolObject(self):
        site = self.context.portal_url.getPortalObject()
        if site.portal_types.School in site.allowedContentTypes():
            return True
        return False

    def getDivisionDescriptor(self):
        return self.context.portal_properties.educommons_properties.getProperty('division_descriptor')

    def getDivisions(self):
        divs =  ['Mathematics', 'Computer Science', 'Instructional Technology',
                 'Decorating']
        
        return divs

    def getTemplates(self):
        return [_(u'Syllabus'), _(u'Course Schedule'), _(u'About the Professor')]



class AddForm(base.NullAddForm):
    """ Add Form """

    form_fields = Fields(ICourseBuilderPortlet)

    def create(self):
        return Assignment()


