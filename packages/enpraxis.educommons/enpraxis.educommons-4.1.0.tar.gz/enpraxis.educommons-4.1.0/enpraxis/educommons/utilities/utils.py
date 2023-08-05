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

from OFS.SimpleItem import SimpleItem
from zope.interface import implements
from interfaces import IECUtility
from collective.contentlicensing.DublinCoreExtensions.interfaces import ILicensable, ILicense
from Acquisition import aq_parent

class eduCommonsUtility(SimpleItem):
    """ Content Licensing Utility """

    implements(IECUtility)


    def FindECParent(self, context):
        """ return titles and ids for the supported licenses. """
        parent = getattr(context.aq_inner, 'getECParent', None)
        if parent:
            return parent()
        else:
            return context.portal_url


    def getFullCourseTitle(self, brain):
        """ Returns the Title with Term and ID information  """
        full_title = ''

        id = brain.getCourseId
        if id:
            full_title = '%s - ' %id
        full_title += brain.Title
        term = brain.getTerm
        if term:
            full_title += ', %s' %term

        return full_title

myECUtil = eduCommonsUtility()
