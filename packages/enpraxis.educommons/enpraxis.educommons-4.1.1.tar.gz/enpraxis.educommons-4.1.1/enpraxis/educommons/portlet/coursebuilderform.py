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

from zope.interface import Interface
from zope.schema import TextLine, Choice, Tuple
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
from plone.app.form.base import AddForm
from zope.formlib.form import FormFields, action
from zope.app.form.browser import FileWidget
from zope.app.form.interfaces import WidgetInputError
from Products.CMFPlone import PloneMessageFactory
from enpraxis.educommons import eduCommonsMessageFactory as _
from enpraxis.educommons.annotations.interfaces import ICourseOrderable, ICourseOrder
from Products.CMFCore.utils import getToolByName
from collective.imstransport.browser.importform import ZipFileLine
from collective.imstransport.utilities.interfaces import IIMSTransportUtility
from zope.schema.interfaces import IVocabularyFactory
from zope.component import getUtility

from customwidgets import EitherOrWidget, ChoiceRadioWidget, MultiPreSelectCheckBoxVocabularyWidget
from customwidgets import EitherOrNoValidateWidget


def schoolsvocab(context):
    portal = context.portal_url.getPortalObject()
    brains = portal.portal_catalog.searchResults(path={'query':'/'.join(portal.getPhysicalPath())+'/',},
                                                 Type='School',
                                                 sort_on='sortable_title')
    return SimpleVocabulary([SimpleVocabulary.createTerm(x.getPath(), x.getPath(), x.Title.decode('utf-8')) for x in brains])


def divisionsvocab(context):
    """ Get the list of current divisions and return it as a vocabulary. """
    portal = context.portal_url.getPortalObject()
    brains = portal.portal_catalog.searchResults(path={'query':'/'.join(portal.getPhysicalPath())+'/',}, 
                                                       Type='Division', 
                                                       sort_on='sortable_title')
    return SimpleVocabulary([SimpleVocabulary.createTerm(x.getPath(), x.getPath(), x.Title.decode('utf-8')) for x in brains])


def coursetemplatevocab(context):
    """ Get list of course templates and return them as a vocabulary. """
    templates = context.portal_actions.template_buttons
    terms = []

    ts = getToolByName(context, 'translation_service')
    for x in templates.items():
        # Only get templates related to courses
        if 'object/search_view/isPageInEduCourse' == x[1].available_expr:
            terms.append(SimpleTerm(x[0], title=ts.translate(msgid=x[1].title,
                                                             domain="eduCommons",
                                                             context=context)))
    return SimpleVocabulary(terms)


def validate_coursebuilder(form, action, data):
    """ Validate the course builder form. """
    school = None
    newschool = None
    division = form.request.form['form.division']
    newdivision = form.request.form['form.newdivision']

    if 'form.school' in form.request.keys():
        school = form.request.form['form.school']
        newschool = form.request.form['form.newschool']
        
    if newschool:
        # Check that the school does not already exist
        brains = form.context.portal_catalog.searchResults(Type='School')
        if brains and newschool in [x.Title.decode('utf-8') for x in brains]:
            sw = form.widgets.get('school')
            sw._error = WidgetInputError(form.context.__name__, 
                                         sw.label, 
                                         _(u'School with the same title already exists.'))
            return sw._error

    if newschool and newdivision:
        # new school and new division, no checks
        pass
    elif newschool and not newdivision:
        # new school and existing division
        # Error new school can not have an existing division
        dw = form.widgets.get('division')
        dw._error = WidgetInputError(form.context.__name__, 
                                     dw.label, 
                                     _(u'Cannot locate Division in yet to be created School object. Please specify a new Division object instead.'))
        return dw._error            
    elif school and newdivision:
        # existing school and new division:
        # Check that the division does not already exist in school
        brains = form.context.portal_catalog.searchResults(path={'query':school+'/'}, 
                                                           Type='Division')
        if brains and newdivision in [x.Title.decode('utf-8') for x in brains]:
            dw = form.widgets.get('division')
            dw._error = WidgetInputError(form.context.__name__, 
                                         dw.label, 
                                         _(u'Division with the same title already exists.'))
            return dw._error            
    elif school and division:
        # existing school and existing division, no checks
        pass
    elif newdivision:
        # no school, new division:
        # check that new division does not exist at the root level
        portal = form.context.portal_url.getPortalObject()
        brains = portal.portal_catalog.searchResults(path={'query':'/'.join(portal.getPhysicalPath())+'/',},
                                                     Type='Division')
        if brains and newdivision in [x.Title.decode('utf-8') for x in brains]:
            dw = form.widgets.get('division')
            dw._error = WidgetInputError(form.context.__name__, 
                                         dw.label, 
                                         _(u'Division with the same title already exists.'))
            return dw._error            
    elif division:
        # no school, existing division, no checks
        pass
    else:
        # no school, no division: Error must specify a division
        dw = form.widgets.get('division')
        dw._error = WidgetInputError(form.context.__name__, dw.label, _(u'Missing division.'))
        return dw._error

    coursename = form.request.form['form.coursename']
    if not coursename:
        cnw = form.widgets.get('coursename')
        cnw._error = WidgetInputError(form.context.__name__, cnw.label, _(u'Missing course name.'))
        return cnw._error


class ICourseBuilderForm(Interface):
    """ Interface for Course Builder Display form """

    school = Choice(title=_(u'School'),
                    required=False,
                    vocabulary='eduCommons.schoolsvocab')

    division = Choice(title=_(u'Division'),
                      required=False,
                      vocabulary='eduCommons.divisionsvocab')

    coursename = TextLine(title=_(u'Course Title') )
    
    courseid = TextLine(title=_(u'Course ID'),
                        description=_(u'The course identifier or catalog number.'),
                        required=False)
    
    courseterm = TextLine(title=_(u'Term'),
                          description=_(u'The term the course was taught in.'),
                          required=False)

    templates = Tuple(title=_(u'Templates'),
                      description=_(u'Choose from the following templates:'),
                      required=False,
                      missing_value=tuple(),
                      value_type=Choice(vocabulary='eduCommons.coursetemplatevocab'))


    filename = ZipFileLine(title=_(u"IMS File Import"),
                           description=_(u"The name of the ims package on your local machine."),
                           required=False)


    packagetype = Choice(title=_(u"Package Type"),
                         description=_(u"The type of the ims package being uploaded"),
                         required=False,
                         vocabulary="imsreadertypevocab")


class CourseBuilderForm(AddForm):
    """ Adapter to adapt a Portlet renderer to a Page form """

    form_fields = FormFields(ICourseBuilderForm).select(
        'division',
        'coursename',
        'courseid',
        'courseterm',
        'templates',
        'filename',
        'packagetype',)
    form_fields['division'].custom_widget = EitherOrWidget
    form_fields['templates'].custom_widget = MultiPreSelectCheckBoxVocabularyWidget
    form_fields['filename'].custom_widget = FileWidget
    form_fields['packagetype'].custom_widget = ChoiceRadioWidget

    label = _(u'Build a Course')
    description = _(u'Create a new course using the fields below.')

    def __init__(self, context, request):
        super(CourseBuilderForm, self).__init__(context, request)
        tmps = context.portal_actions.template_buttons
        self.templates = dict([(x[0],x[1].title) for x in tmps.objectItems()])
        self.plone_utils = getToolByName(self.context, 'plone_utils')
        self.ims_util = getUtility(IIMSTransportUtility)

    def createObject(self, parent, objtype, title, templateid, pos, **kw):
        objid = self.plone_utils.normalizeString(title)
        objid = self.context.generateUniqueId(objid)
        objid = parent.invokeFactory(objtype, id=objid, title=title )
        context = getattr(parent, objid)
        template = context.restrictedTraverse('@@' + str(templateid))
        context.edit(title=title,
                     Text=template(context),
                     text=template(context),
                     **kw)
        context._renameAfterCreation()
        if 'syllabus_view' == templateid:
            context.setPresentation(True)
            mut = context.Schema()['oerType'].getMutator(context)
            mut(['Syllabus'])
        elif 'schedule_view' == templateid:
            mut = context.Schema()['oerType'].getMutator(context)
            mut(['Schedule'])
        if pos != -1:
            if ICourseOrderable.providedBy(context):
                cobj = ICourseOrder(context)
                cobj.position = pos
        context.reindexObject()
        return context

    def buildCourse(self, context):
        # Get existing division, or create a new one
        divname = self.request.form['form.division']
        newdivision = self.request.form['form.newdivision']

        if newdivision:
            division = self.createObject(context, 
                                         'Division', 
                                         newdivision.encode('utf-8'), 
                                         'division_view',
                                         -1)
        else:
            division = None
            brains = self.context.portal_catalog.searchResults(path={'query':divname,},
                                                               id=divname.split('/')[-1])
            if brains and len(brains) > 0:
                division = brains[0].getObject()

        if not division:
            self.status = _(u'Could not create/find existing division.')
            return None

        # Create a new course
        course = self.createObject(division, 
                                   'Course', 
                                   self.request.form['form.coursename'],
                                   'course_view',
                                   0,
                                   courseId=self.request.form['form.courseid'],
                                   term=self.request.form['form.courseterm'],)

        if not course:
            self.status = _(u'Could not create course.')
            return None

        # Create default templates
        templates = ''
        if self.request.form.has_key('form.templates'):
            templates = self.request.form['form.templates']

        # Determine if a singular or multiple templates are returned
        if type(templates) == type(u''):
            self.createObject(course, 'Document', self.templates[templates], templates)
        elif type(templates) == type([]):
            count = 1
            for x in self.request.form['form.templates']:
                ts = getToolByName(context, 'translation_service')
                title = ts.translate(msgid=self.templates[x],
                                     domain="eduCommons",
                                     context=self)
                self.createObject(course, 'Document', title, x, count)
                count += 1

        # Get IMS file
        filename = ''
        packagetype = ''

        if self.request.form.has_key('form.filename'):
            filename = self.request.form['form.filename']

        if self.request.form.has_key('form.packagetype'):
            packagetype = self.request.form['form.packagetype']

        if filename != '' and packagetype != '':
            imsvocab = getUtility(IVocabularyFactory, name='imsreadertypevocab')(self.context)
            package_xform = imsvocab.getTermByToken(packagetype).value
            self.ims_util.importPackage(course,filename,package_xform) 

        return course


    def getSchool(self):
        """ Get a current school object, if none selected create one """
        schname = self.request.form['form.school']
        newschool = self.request.form['form.newschool']

        if newschool:
            school = self.createObject(self.context, 
                                       'School', 
                                       newschool.encode('utf-8'), 
                                       'school_view',
                                       -1)
        else:
            school = None
            brains = self.context.portal_catalog.searchResults(path={'query':schname,},
                                                                id=schname.split('/')[-1])
            if brains and len(brains) > 0:
                school = brains[0].getObject()

        if not school:
            self.status = _(u'Could not create/find existing school.')
            return None

        return school


    @action(PloneMessageFactory(u'Submit'), 
            validator=validate_coursebuilder,
            name=u'Submit')
    def action_submit(self, action, data): 
        """ Create a course. """

        if 'form.school' in action.form.request.keys():
            school = self.getSchool()
            if school:
                course = self.buildCourse(school)
                self.request.RESPONSE.redirect(course.absolute_url() + '/edit')
        else:
            course = self.buildCourse(self.context)
            self.request.RESPONSE.redirect(course.absolute_url() + '/edit')


class SCourseBuilderForm(CourseBuilderForm):
    """ Course Builder Form with School Object """

    form_fields = FormFields(ICourseBuilderForm)
    form_fields['school'].custom_widget = EitherOrWidget        
    form_fields['division'].custom_widget = EitherOrNoValidateWidget
    form_fields['templates'].custom_widget = MultiPreSelectCheckBoxVocabularyWidget
    form_fields['filename'].custom_widget = FileWidget
    form_fields['packagetype'].custom_widget = ChoiceRadioWidget

