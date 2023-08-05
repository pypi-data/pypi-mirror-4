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

from zope.formlib.form import PageForm, FormFields, action
from zope.app.form.interfaces import WidgetInputError
from zope.component import getMultiAdapter
from Products.PageTemplates import PageTemplateFile
from enpraxis.educommons import eduCommonsMessageFactory as _
from Products.MailHost.MailHost import MailHostError
from Products.statusmessages.interfaces import IStatusMessage
from interfaces import ITemplateForm

from Products.CMFDefault.formlib.widgets import ChoiceRadioWidget

from zope.interface import implements
from zope.component import getUtility
from zope.schema.vocabulary import SimpleVocabulary



def templateVocabulary(context):
    template_actions = context.portal_actions.listActionInfos(object=context, categories=('template_buttons'))
    items = ()
    for template_action in template_actions:
        id = template_action['id']
        title = str(template_action['title'])
        items += (title, id), 
        
    return SimpleVocabulary.fromItems(items)


class TemplateForm(PageForm):
    """ A form for selecting templates on objects """

    form_fields = FormFields(ITemplateForm)
    form_fields['template'].custom_widget = ChoiceRadioWidget

    label = u'Template Chooser'
    description = u'Preview and choose templates for your content object'

    @action(_(u'Apply Templates', default=u'Apply Templates'), 
            name=u'Submit')
    def action_submit(self, action, data):
        # Apply the template
        if data.has_key('template') and data['template']:
            context = self.context
            template = '@@%s' % data['template']
            template = context.restrictedTraverse(str(template))
            text = template(context)
            context.setText(text)
            if 'syllabus_view' == data['template']:
                context.setPresentation(True)
                context.setExcludeFromNav(False)
                mut = self.context.Schema()['oerType'].getMutator(self.context)
                mut(['Syllabus'])                    
            elif 'schedule_view' == data['template']:
                context.setExcludeFromNav(False)
                mut = self.context.Schema()['oerType'].getMutator(self.context)
                mut(['Schedule'])                    
            elif 'aboutprof_view' == data['template']:
                context.setExcludeFromNav(False)
                mut = self.context.Schema()['oerType'].getMutator(self.context)
                mut([''])                    
            context.reindexObject()
            self.request.response.redirect('view')

        return ''

    
