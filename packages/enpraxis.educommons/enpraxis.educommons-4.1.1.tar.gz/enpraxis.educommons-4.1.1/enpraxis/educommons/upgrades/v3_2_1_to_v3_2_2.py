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

from StringIO import StringIO
from Products.CMFCore.utils import getToolByName
from Products.ATContentTypes.content.schemata import finalizeATCTSchema
from Products.CMFCore.ActionInformation import Action
from Products.contentmigration.walker import CustomQueryWalker
from Products.contentmigration.migrator import InlineFieldActionMigrator

PROFILE_ID = 'profile-enpraxis.educommons:default'


def convertCrossListedField(obj, val, **kw):
    """ Reference field does not set properly if we just return a list of UIDs.
        Instead we just return an empty tuple and call the setCrosslisting() function
        expliciltly, which seems to work fine. """

    if val:
        portal_url = getToolByName(obj, 'portal_url')
        portal = portal_url.getPortalObject()
        if val:
            brains = portal.portal_catalog(path={'query':'/'.join(portal.getPhysicalPath())+'/'},
                                           id=val)
            if brains:
                obj.setCrosslisting([x.UID for x in brains])
    return ()


class CrossListingMigrator(InlineFieldActionMigrator):
    """ Migrate crosslisting to a proper ReferenceField, with the same equivalent values
        that the old ListField had. """

    src_portal_type = 'Course'
    src_meta_type = 'Course'

    fieldActions = ({ 'fieldName' : 'crosslisting',
                      'transform' : convertCrossListedField,
                      },
                    )


def updateCourses(portal):
    """ Migrate current courses in ZODB  """

    walker = CustomQueryWalker(portal, 
                               CrossListingMigrator, 
                               query={})
    walker.go()


def migrate(portal_setup):
    """ Migration from eduCommons 3.1.1 to 3.2.1  """

    portal_url = getToolByName(portal_setup, 'portal_url')
    portal = portal_url.getPortalObject()    
    ec_props = portal.portal_properties.educommons_properties
    
    # Add school_descriptor property to educommons_properties
    if not getattr(ec_props, 'school_descriptor', None):
        ec_props.manage_addProperty(id='school_descriptor', type='string', value='Schools')
    
    # Rerun actions profile to update new action definitions
    portal_setup.runImportStepFromProfile(PROFILE_ID, 'actions')

    # Setup new browser layer so that our schemaextensions will work
    portal_setup.runImportStepFromProfile(PROFILE_ID, 'browserlayer')

    # Update course objects to handle new fields correctly
    updateCourses(portal)
