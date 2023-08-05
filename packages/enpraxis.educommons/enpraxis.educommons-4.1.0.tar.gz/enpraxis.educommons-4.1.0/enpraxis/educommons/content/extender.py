from Products.Archetypes.public import StringField
from Products.Archetypes.atapi import MultiSelectionWidget
from archetypes.schemaextender.field import ExtensionField
from zope.component import adapts
from zope.interface import implements
from archetypes.schemaextender.interfaces import ISchemaExtender, IBrowserLayerAwareExtender
from Products.Archetypes.public import BooleanWidget
from Products.ATContentTypes.interface import IATDocument
from enpraxis.educommons import eduCommonsMessageFactory as _
from enpraxis.educommons.interfaces import IeduCommonsBrowserLayer


oer_type_vocab = [
    ('Syllabus', _(u'Syllabus')),
    ('Schedule', _(u'Schedule')),
    ('Lecture Notes', _(u'Lecture Notes')),
    ('Assignment', _(u'Assignment')),
    ('Project', _(u'Project')),
    ('Readings', _(u'Readings')),
    ('Image Gallery', _(u'Image Gallery')),
    ('Video', _(u'Video')),
    ('Audio', _(u'Audio')),
    ('Interactive', _(u'Interactive')),
    ('Textbook', _(u'Textbook')),
    ]
        
         
class OERTypeField(ExtensionField, StringField):
    """ A string field added to basic archetypes. """


class OERTypeExtender(object):
    """ An extension to default archetypes schemas for basic objects. """

    adapts(IATDocument)
    implements(ISchemaExtender, IBrowserLayerAwareExtender)
    layer = IeduCommonsBrowserLayer

    fields = [
        OERTypeField('oerType',
                     required=False,
                     isMetadata=True,
                     vocabulary=oer_type_vocab,
                     default=None,
                     widget=MultiSelectionWidget(
                         label=_(u'OER Type'),
                         label_msgid='label_oer_type',
                         description=_(u'The type of resourse'),
                         description_msgid=_(u'help_oer_type'),
                         format='select',
                         ),
                     ),
        ]

    def __init__(self, context):
        self.context = context
        
    def getFields(self):
        return self.fields

                                            
