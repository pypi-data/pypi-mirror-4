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

from Products.Archetypes.atapi import AnnotationStorage
from Products.ATContentTypes.configuration import zconf
from Products.ATContentTypes.atct import ATFolder, ATFolderSchema
from Products.ATContentTypes.lib.historyaware import HistoryAwareMixin
from Products.ATContentTypes.content.base import registerATCT
from Products.ATContentTypes.content.schemata import finalizeATCTSchema
from zope.interface import implements
from AccessControl import ClassSecurityInfo
from Products.CMFCore.permissions import AddPortalContent
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from enpraxis.educommons.interfaces import IFeedback
from enpraxis.educommons.config import PROJECTNAME



FeedbackSchema = ATFolderSchema.copy()

finalizeATCTSchema(FeedbackSchema)
        


class Feedback(ATFolder):
    """ The Feedback content object. """

    implements(IFeedback)
    security = ClassSecurityInfo()
    schema = FeedbackSchema
    portal_type = "Feedback"

    _at_rename_after_creation = True


    def initializeArchetype(self, **kwargs):
        ATFolder.initializeArchetype(self, **kwargs)
        self.setLayout('feedback_view')

registerATCT(Feedback, PROJECTNAME)
