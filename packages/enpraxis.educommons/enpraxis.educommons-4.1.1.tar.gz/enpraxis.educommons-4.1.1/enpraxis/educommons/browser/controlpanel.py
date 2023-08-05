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

from zope.interface import Interface, implements
from zope.component import adapts, getUtility
from zope.formlib.form import FormFields
from zope.schema import TextLine, List, Bool
from Products.CMFDefault.formlib.schema import SchemaAdapterBase
from Products.CMFPlone.interfaces import IPloneSiteRoot
from Products.CMFCore.interfaces import IPropertiesTool
from plone.app.controlpanel.form import ControlPanelForm
from enpraxis.educommons import eduCommonsMessageFactory as _

class IeduCommonsSchema(Interface):

    school_enable = Bool(title=_(u'Enable Schools'),
                         description=_(u'Enable support for school objects '
                                       'which encapsulate divisions.'),
                         default=False)
                         

    school_descriptor = TextLine(title=_(u'School Descriptor'),
                                   description=_(u"A descriptor that describes how your "
                                                 "institutions are divided. Typically "
                                                 "this will be 'Schools' or 'Universities.'"),
                                   required=True)

    
    division_descriptor = TextLine(title=_(u'Division Descriptor'),
                                   description=_(u"A descriptor that describes how your "
                                                 "academic institution is divided. Typically "
                                                 "this will be 'Departments' or 'Divisions.'"),
                                   required=True)

    course_descriptor = TextLine(title=_(u'Course Descriptor'),
                                 description=_(u'A descriptor that describes courses '
                                               'in your institution.'),
                                 required=True)

    oerrecommender_enabled = Bool(title=_(u'OER Recommender'),
                                  description=_(u'Enable the display of the OER Recommender Portlet for Course objects and sub-objects.'),
                                  default=False,
                                  required=True)

    reusecourse_enabled = Bool(title=_(u'Allow Reuse Course Export'),
                                  description=_(u'Enable the display of the course export link for Course objects and sub-objects.'),
                                  default=False,
                                  required=True)


    reusecourse_instance = TextLine(title=_('Reuse Course Portal'),
                                    description=_(u'The URL to the eduCommons instance utilized by the Reuse Course portlet.'),
                                    required=True)
                                    
    workflow_order = List(title=_(u'Workflow Order'),
                      description=_(u"This setting is utilized in the Course Summary Portlet, allowing the portlet to render workflow states "
                                     "in the proper procedural order. If you utilize a non-standard workflow for content objects, you will need "
                                     "to modify this setting in order for the portlet to render the non-standard states."),
                      required=True,
                      value_type=TextLine(),)



class eduCommonsControlPanelAdapter(SchemaAdapterBase):
    """ Control Panel Adapter """

    adapts(IPloneSiteRoot)
    implements(IeduCommonsSchema)

    def __init__(self, context):
        super(eduCommonsControlPanelAdapter, self).__init__(context)
        self.props = getUtility(IPropertiesTool)
        self.ecprops = self.props.educommons_properties

    def get_school_enable(self):
        return self.context.portal_types.School in self.context.allowedContentTypes()

    def set_school_enable(self, school):
        enabled = self.get_school_enable()
        pt = getattr(self.context.portal_types, 'Plone Site', None)
        ecprops = self.context.portal_properties.educommons_properties
        if pt:
            atypes = list(pt.getProperty('allowed_content_types'))
            if school and not enabled:
                # Enable school object
                atypes.append('School')
                pt.manage_changeProperties(allowed_content_types=atypes)
                ecprops.manage_changeProperties(school_enable=True)
            elif not school and enabled:
                # Disable school object
                atypes.remove('School')
                pt.manage_changeProperties(allowed_content_types=atypes)
                ecprops.manage_changeProperties(school_enable=False)

    def get_school_descriptor(self):
        return self.ecprops.getProperty('school_descriptor')

    def set_school_descriptor(self, descriptor):
        self.ecprops.manage_changeProperties(school_descriptor=descriptor)

    def get_division_descriptor(self):
        return self.ecprops.getProperty('division_descriptor')

    def set_division_descriptor(self, descriptor):
        self.ecprops.manage_changeProperties(division_descriptor=descriptor)

    def get_course_descriptor(self):
        return self.ecprops.getProperty('course_descriptor')

    def set_course_descriptor(self, descriptor):
        self.ecprops.manage_changeProperties(course_descriptor=descriptor)

    def get_oerrecommender_enabled(self):
        return self.ecprops.getProperty('oerrecommender_enabled')

    def set_oerrecommender_enabled(self, oerrecommender):
        self.ecprops.manage_changeProperties(oerrecommender_enabled=oerrecommender)

    def get_reusecourse_enabled(self):
        return self.ecprops.getProperty('reusecourse_enabled')

    def set_reusecourse_enabled(self, reusecourse_enable):
        self.ecprops.manage_changeProperties(reusecourse_enabled=reusecourse_enable)

    def get_reusecourse_instance(self):
        return self.ecprops.getProperty('reusecourse_instance')

    def set_reusecourse_instance(self, reusecourse):
        self.ecprops.manage_changeProperties(reusecourse_instance=reusecourse)

    def get_workflow_order(self):
        return self.ecprops.workflow_order

    def set_workflow_order(self, wf_order):
        self.ecprops.workflow_order = wf_order        

    school_enable = property(get_school_enable, set_school_enable)
    school_descriptor = property(get_school_descriptor, set_school_descriptor)
    division_descriptor = property(get_division_descriptor, set_division_descriptor)
    course_descriptor = property(get_course_descriptor, set_course_descriptor)
    oerrecommender_enabled = property(get_oerrecommender_enabled, set_oerrecommender_enabled)
    reusecourse_enabled = property(get_reusecourse_enabled, set_reusecourse_enabled)
    reusecourse_instance = property(get_reusecourse_instance, set_reusecourse_instance)
    workflow_order = property(get_workflow_order, set_workflow_order)

class eduCommonsControlPanel(ControlPanelForm):

    form_fields = FormFields(IeduCommonsSchema)
    
    label = _(u'eduCommons Settings')
    description = _(u'Settings which control how eduCommons looks and functions.')
    form_name = _(u'eduCommons Settings')
