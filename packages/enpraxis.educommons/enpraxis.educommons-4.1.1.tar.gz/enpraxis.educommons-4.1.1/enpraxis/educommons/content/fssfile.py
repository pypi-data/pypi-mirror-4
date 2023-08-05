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

from AccessControl import ClassSecurityInfo
from zope.interface import implements

# Archetypes imports
try:
    from Products.LinguaPlone.public import *
except ImportError: 
    # No multilingual support
    from Products.Archetypes.public import *

# Products imports
from iw.fss.FileSystemStorage import FileSystemStorage
from Products.ATContentTypes.atct import ATFile, ATFileSchema
from Products.ATContentTypes.lib.historyaware import HistoryAwareMixin
from Products.ATContentTypes.content.base import registerATCT
from Products.ATContentTypes.content.schemata import finalizeATCTSchema

from enpraxis.educommons.interfaces import IFSSFile
from enpraxis.educommons.config import PROJECTNAME


from Products.CMFPlone import PloneMessageFactory as _

FSSFileSchema = ATFileSchema.copy() + Schema((
    FileField('file',
              required=False,
              primary=True,
              storage=FileSystemStorage(),
              widget = FileWidget(
                        description = u"Select the file to be added by clicking the 'Browse' button.",
                        description_msgid = "help_file",
                        label= "Large File",
                        label_msgid = "label_large_file",
                        i18n_domain = "eduCommons",
                        show_content_type = False,)),
    ), 
    marshall=RFC822Marshaller()
)
                                           
finalizeATCTSchema(FSSFileSchema)

class FSSFile(ATFile):
    """A storage item for IMS/ZIP copies of courses using FileSystemStorage"""

    implements(IFSSFile)
    
    security = ClassSecurityInfo()
    schema = FSSFileSchema
    portal_type = 'Large File'
    
    _at_rename_after_creation = True

    def initializeArchetype(self, **kwargs):
        ATFile.initializeArchetype(self, **kwargs)


registerATCT(FSSFile, PROJECTNAME)
