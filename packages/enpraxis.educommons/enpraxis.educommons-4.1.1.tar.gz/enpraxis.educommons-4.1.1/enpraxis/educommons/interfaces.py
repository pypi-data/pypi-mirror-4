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

from plone.theme.interfaces import IDefaultPloneLayer
from zope.interface import Interface
from zope.annotation.interfaces import IAnnotatable
from zope.component.interfaces import IObjectEvent

class IeduCommonsBrowserLayer(IDefaultPloneLayer):
    """ Marker interface for eduCommons Plone layer """

class IPortalObject(Interface):
    """  Marker interface for the Portal Object """

class ICoursesTopic(Interface):
    """ Marker interface for Courses Topic, which implements the course list. """

class IDivision(Interface):
    """ Marker interface for Division object type. """

class ICourse(Interface):
    """ Marker interface for Course object type. """

class IFSSFile(Interface):
    """ Marker interface for FSSFile object type. """

class IFeedback(Interface):
    """ Marker interface for Feedback object type.  """

class ISchool(Interface):
    """ Marker interface for School object type. """


#class IClearCopyrightable(IAnnotatable):
#    """ Marker interface  """

#class IAccessibilityCompliantable(IAnnotatable):
#    """ Marker interface  """

#class ICourseOrderable(IAnnotatable):
#    """ Marker interface """

#class IClearCopyright(Interface):
#    """ Cleared Copyright interface  """

#    def getClearedCopyright():
#        """ Get the Cleared Copyright value  """

#    def setClearedCopyright():
#        """ Set the Cleared Copyright value  """

#class IAccessibilityCompliant(Interface):
#    """ Accessibility Compliant interface  """

#    def getAccessibilityCompliant():
#        """ Get the accessibility Compliant value  """

#    def setAccessibilityCompliant():
#        """ Set the accessibility Compliant value  """

class IOpenOCWSite(Interface):
    """ Marker interface to mark eduCommons site as an OpenOCW site. """

class ICourseUpdateEvent(IObjectEvent):
    """ Fire a Course Update Event """

class IDeleteCourseObjectEvent(IObjectEvent):
    """ Fire an event when an object is deleted """
