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

from Products.Archetypes.atapi import Schema
from Products.Archetypes.atapi import TextField, TextAreaWidget, RichWidget
from Products.Archetypes.atapi import StringField, StringWidget, LinesField, ReferenceField
from Products.Archetypes.atapi import BooleanField, BooleanWidget
from Products.Archetypes.atapi import SelectionWidget, MultiSelectionWidget
from enpraxis.educommons.content.countryvocab import country_vocab
from enpraxis.educommons.content.extender import oer_type_vocab
from Products.Archetypes.atapi import AnnotationStorage
from Products.Archetypes.atapi import RFC822Marshaller
from Products.Archetypes.utils import DisplayList
from Products.ATContentTypes.configuration import zconf
from Products.ATContentTypes.atct import ATFolder, ATFolderSchema
from Products.ATContentTypes.lib.historyaware import HistoryAwareMixin
from Products.ATContentTypes.content.base import registerATCT
from Products.ATContentTypes.content.schemata import finalizeATCTSchema
from zope.interface import implements
from AccessControl import ClassSecurityInfo
from Products.CMFCore.permissions import AddPortalContent
from enpraxis.educommons.interfaces import ICourse
from enpraxis.educommons.config import PROJECTNAME

from enpraxis.educommons import eduCommonsMessageFactory as _


CourseSchema = ATFolderSchema.copy() + Schema((
        
    TextField('text',
              required=False,
              searchable=True,
              primary=True,
              storage = AnnotationStorage(migrate=True),
              validators = ('isTidyHtmlWithCleanup',),
              #validators = ('isTidyHtml',),
              default_output_type = 'text/x-html-safe',
              widget = RichWidget(
                        description = '',
                        label = _(u'Body Text'),
                        rows = 25,
                        allow_file_upload = zconf.ATDocument.allow_document_upload),
             ),

    StringField('courseId',
                required=False,
                widget=StringWidget(label=_(u'Course ID'),
                                    label_msgid='label_course_id',
                        	    description=_(u'The course identifier or catalog number. Also can be used to sequence courses (1.0, 2.0, etc).'),
                                    description_msgid='help_course_id',
                                    ),
                ),

    StringField('term',
                required=False,
                widget=StringWidget(label=_(u'Term'),
                                    label_msgid='label_course_term',
                                    description=_(u'The term the course was taught in.'),
                                    description_msgid='help_course_term',
                                    ),
                ),
        

    TextField('structure',
              required=False,
              default_content_type='text/plain',
              allowable_content_types = ('text/plain',),
              widget=TextAreaWidget(label=_(u'Structure'),
                                    label_msgid='label_course_structure',
                                    description=_(u'The structure of the course.'),
                                    description_msgid='help_course_structure',
                                    rows=3,
                                    cols=40,
                                    ),
              ),

    StringField('level',
                required=False,
                vocabulary=[_(u'Not Specified'), _(u'Undergraduate'), _(u'Graduate'), _(u'Both')],
                widget=SelectionWidget(label=_(u'Level'),
                                       label_msgid='label_course_structure',
                                       description=_(u'The level at which the course is taught.'),
                                       description_msgid='help_course_level',
                                       format='select',
                                       ),
                ),

    ReferenceField('crosslisting',
                   required=False,
                   multiValued=True,
                   relationship='crosslisted-in',
                   allowed_types=('Division',),
                   vocabulary='getDivisionsVocab',
                   widget=MultiSelectionWidget(label=_(u'Cross Listing(s)'),
                                               label_msgid='label_course_crosslisting',
                                               description=_(u'Other Divisions that this Course '
                                                             'should be listed in. To select '
                                                             'multiple options, SHIFT click for '
                                                             'adjacent items, or CTRL/CMD click '
                                                             'for non-adjacent items. To remove '
                                                             'all cross listings deselect all '
                                                             'entries.'),
                                               description_msgid='help_course_crosslisting',
                                               format='select',
                                               ),
                   ),

#    StringField('institutionName',
#                required=False,
#                widget=StringWidget(label=_(u'Institution Name'),
#                                    label_msgid='label_course_institution_name',
#                                    description=_(u'The name of the univeristy, institution '
#                                                  'or business responsible for this course.'),
#                                    description_msgid='help_course_instructor_name',
#                                    ),
#                ),
    
#    BooleanField('institutionEducation',
#                 widget=BooleanWidget(label=_(u'Institution Function'),
#                                      label_msgid='label_course_institution_edu',
#                                      description=_(u'Is the primary function of this institution '
#                                                    'based on education?'),
#                                      description_msgid='help_course_institution_edu',
#                                      ),
#                 ),

#    StringField('country',
#                required=False,
#                vocabulary=country_vocab,
#                widget=SelectionWidget(label=_(u'Country of Origin'),
#                                       label_msgid='label_course_country',
#                                       description=_(u'The country of origin for the course.'),
#                                       description_msgid='help_course_country',
#                                    ),
#                ),
    
#    StringField('institutionCourseId',
#                required=False,
#                widget=StringWidget(label=_(u'Institutional Course ID'),
#                                    label_msgid='label_course_institution_course_id',
#                                    description=_(u'The course ID as assigned by the institution '
#                                                  '(leave blank if the original course ID is '
#                                                  'the same as the institution ID)'),
#                                    description_msgid='help_course_institution_course_id',
#                                    ),
#                ),

    StringField('instructorName',
                required=False,
                widget=StringWidget(label=_(u'Instructor Name'),
                                    label_msgid='label_course_instructor_name',
                                    description=_(u'The name of the primary instructor '
                                                  'teaching this course.'),
                                    description_msgid='help_course_instructor_name',
                                    ),
                ),
    
    StringField('instructorEmail',
                required=False,
                widget=StringWidget(label=_(u'Instructor Email'),
                                    label_msgid='label_course_instructor_email',
                                    description=_(u'The email address of the primary '
                                                  'instructor teaching this course.'),
                                    description_msgid='help_course_instructor_email',
                                    ),
                ),

    BooleanField('displayInstEmail',
                 widget=BooleanWidget(label=_(u'Display Instructor Email Address'),
                                      label_msgid='label_course_display_inst_email',
                                      description=_(u'Should the primary instructor\'s '
                                                    'Email address be publically displayed?'),
                                      description_msgid='help_course_display_inst_email',
                                      ),
                 ),

    BooleanField('instructorAsCreator',
                 widget=BooleanWidget(label=_(u'Instructor is Primary Author'),
                                      label_msgid='label_course_inst_primary_author',
                                      description=_(u'Is the primary instructor also the '
                                                    'primary author of the course materials?'),
                                      description_msgid='help_course_inst_primary_author',
                                      ),
                 ),

    BooleanField('exemplaryCourse',
                 widget=BooleanWidget(label=_(u'Exemplary Course'),
                                      label_msgid='label_course_exemplary',
                                      description=_(u'Mark/unmark this course as exemplary.'),
                                      description_msgid='help_course_exemplary',
                                      ),
                 ),

    ),
    marshall=RFC822Marshaller()
    )

#CourseSchema.changeSchemataForField('institutionName', 'course')
#CourseSchema.changeSchemataForField('institutionEducation', 'course')
#CourseSchema.changeSchemataForField('country', 'course')
#CourseSchema.changeSchemataForField('institutionCourseId', 'course')

#CourseSchema.changeSchemataForField('instructorName', 'course')
#CourseSchema.changeSchemataForField('instructorEmail', 'course')
#CourseSchema.changeSchemataForField('displayInstEmail', 'course')
#CourseSchema.changeSchemataForField('instructorAsCreator', 'course')
#CourseSchema.changeSchemataForField('exemplaryCourse', 'course')

finalizeATCTSchema(CourseSchema)



class Course(ATFolder):
    """ A course content object """

    implements(ICourse)
    security = ClassSecurityInfo()
    schema = CourseSchema
    portal_type = 'Course'

    _at_rename_after_creation = True

    def initializeArchetype(self, **kwargs):
        ATFolder.initializeArchetype(self, **kwargs)
        deftext = self.restrictedTraverse('@@course_view')
        self.setText(deftext())

    def getECParent(self):
        """ Determine by acquisition if an object is a child of a course. """
        return self

    def getDivisionsVocab(self):
        """ Get the list of current divisions and return it as a vocabulary. """
        path = {'query':('/'), }
        brains = self.portal_catalog.searchResults(path=path, 
                                                   Type='Division', 
                                                   sort_on='sortable_title')
        dl = DisplayList()
#        dl.add('None', '')
        for brain in brains:
            if brain.getId != self.aq_parent.id:
                dl.add(brain.UID, brain.Title)
        return dl
        

registerATCT(Course, PROJECTNAME)
