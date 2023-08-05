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
from Products.Archetypes.atapi import TextField, RichWidget
from Products.Archetypes.atapi import AnnotationStorage
from Products.Archetypes.atapi import RFC822Marshaller
from Products.ATContentTypes.configuration import zconf
from Products.ATContentTypes.atct import ATFolder, ATFolderSchema
from Products.ATContentTypes.content.base import registerATCT
from Products.ATContentTypes.content.schemata import finalizeATCTSchema
from AccessControl import ClassSecurityInfo
from enpraxis.educommons.interfaces import IDivision
from enpraxis.educommons.config import PROJECTNAME
from enpraxis.educommons import eduCommonsMessageFactory as _

from zope.interface import implements

DivisionSchema = ATFolderSchema.copy() + Schema((
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
    ),
    marshall=RFC822Marshaller()
    )

finalizeATCTSchema(DivisionSchema)
        


class Division(ATFolder):
    """ The Department/Division content object. """

    implements(IDivision)
    security = ClassSecurityInfo()
    schema = DivisionSchema
    portal_type = "Division"

    _at_rename_after_creation = True


    def initializeArchetype(self, **kwargs):
        ATFolder.initializeArchetype(self, **kwargs)
        deftext = self.restrictedTraverse('@@division_view')
        self.setText(deftext())

    def getECParent(self):
        """ Determine by acquisition if an object is a child of a course. """
        return self

registerATCT(Division, PROJECTNAME)
