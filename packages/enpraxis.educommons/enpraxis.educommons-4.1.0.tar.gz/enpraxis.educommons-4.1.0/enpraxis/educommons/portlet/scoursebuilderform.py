from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
from coursebuilderform import ICourseBuilderForm, CourseBuilderForm
from zope.schema import TextLine, Choice, Tuple
from collective.imstransport.browser.importform import ZipFileLine
from zope.app.form.interfaces import WidgetInputError
from enpraxis.educommons import eduCommonsMessageFactory as _
from Products.CMFPlone import PloneMessageFactory
from zope.formlib.form import FormFields, action
from zope.app.form.browser import FileWidget

from customwidgets import EitherOrWidget, ChoiceRadioWidget, MultiPreSelectCheckBoxVocabularyWidget
from customwidgets import EitherOrNoValidateWidget

def schoolsvocab(context):
    """ Get the list of current schools and return it as a vocabulary. """
    path = {'query':('/'), }
    brains = context.portal_catalog.searchResults(path=path, 
                                                  Type='School', 
                                                  sort_on='sortable_title')
    terms = [SimpleTerm(x.getId, title=x.Title.decode('utf-8') ) for x in brains]

    return SimpleVocabulary(terms)

def divisionsvocab(context):
    """ Get the list of current divisions and return it as a vocabulary. """
    path = {'query':('/'), 'depth':2, }
    brains = context.portal_catalog.searchResults(path=path, 
                                                  Type='Division', 
                                                  sort_on='sortable_title')
    terms = []
    for brain in brains:
        title = brain.Title.decode('utf-8')
        newterm = SimpleTerm(brain.getId, title=title)
        terms += [newterm]

    return SimpleVocabulary(terms)

def validate_scoursebuilder(form, action, data):
    school = form.request.form['form.school']
    newschool = form.request.form['form.newschool']

    if not school and not newschool:
        sw = form.widgets.get('school')
        sw._error = WidgetInputError(form.context.__name__, 
                                     sw.label, 
                                     _(u'Missing school.'))
        return sw._error

    division = form.request.form['form.division']
    newdivision = form.request.form['form.newdivision']
    
    if not division and not newdivision:
        dw = form.widgets.get('division')
        dw._error = WidgetInputError(form.context.__name__, 
                                     dw.label, 
                                     _(u'Missing division.'))
        return dw._error

    return []

class ISCourseBuilderForm(ICourseBuilderForm):
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

class SCourseBuilderForm(CourseBuilderForm):
    """ Course Builder Form with School Object """

    form_fields = FormFields(ISCourseBuilderForm)
    form_fields['school'].custom_widget = EitherOrWidget        
    form_fields['division'].custom_widget = EitherOrNoValidateWidget
    form_fields['templates'].custom_widget = MultiPreSelectCheckBoxVocabularyWidget
    form_fields['filename'].custom_widget = FileWidget
    form_fields['packagetype'].custom_widget = ChoiceRadioWidget


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
            path = {'query':('/'), }
            brains = self.context.portal_catalog.searchResults(path=path, id=schname)
            if brains and len(brains) > 0:
                school = brains[0].getObject()

        if not school:
            self.status = _(u'Could not create/find existing division.')
            return None

        return school

    @action(PloneMessageFactory(u'Submit'), 
            validator=validate_scoursebuilder,
            name=u'Submit')
    def action_submit(self, action, data): 
        """ Create a course. """

        school = self.getSchool()
        if school:
            course = self.buildCourse(school)
                
        # Redirect to the course edit page
        self.request.RESPONSE.redirect(course.absolute_url() + '/edit')


        
