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

from zope.interface import implements
from zope.component import adapts
from interfaces import IClearCopyrightable, IClearCopyright
from interfaces import IAccessibilityCompliant, IAccessibilityCompliantable
from interfaces import ICourseOrderable, ICourseOrder
from zope.annotation.interfaces import IAnnotations
from persistent.mapping import  PersistentMapping


CCKEY = 'eduCommons.clearcopyright'
ACCESSIBLEKEY = 'eduCommons.accessible'
POSITIONKEY = 'eduCommons.positionInCourse'


class ClearCopyright(object):
    """ This class adds a clear copyright fields to content """

    implements(IClearCopyright)

    def __init__(self, context):
        self.context = context
        self.annotations = IAnnotations(context)
        cc = self.annotations.get(CCKEY, None)
        if None == cc:
            self.annotations[CCKEY] = False

    def getClearedCopyright(self):
        """ Get the contents of the clear copyright field. """
        return self.annotations[CCKEY]

    def setClearedCopyright(self, isCC):
        """ Set the clear copyright field. """
        self.annotations[CCKEY] = isCC

    clearedcopyright = property(fget=getClearedCopyright, fset=setClearedCopyright)


class AccessibilityCompliant(object):
    """ This class adds an Accessibility Compliance field to content """

    implements(IAccessibilityCompliant)

    def __init__(self, context):
        self.context = context
        self.annotations = IAnnotations(context)
        accessible = self.annotations.get(ACCESSIBLEKEY, None)
        if None == accessible:
            self.annotations[ACCESSIBLEKEY] = False

    def getAccessible(self):
        """ Get the contents of the accessibility field. """
        return self.annotations[ACCESSIBLEKEY]

    def setAccessible(self, isAccessible):
        """ Set the accessible field. """
        self.annotations[ACCESSIBLEKEY] = isAccessible

    accessible = property(fget=getAccessible, fset=setAccessible)


class PositionInCourse(object):
    """ This class adds a position holder for objects in a course. """

    implements(ICourseOrder)

    def __init__(self, context):
        self.context = context
        self.annotations = IAnnotations(context)
        pos = self.annotations.get(POSITIONKEY, None)
        if None == pos:
            self.annotations[POSITIONKEY] = 0

    def getPositionInCourse(self):
        """ Get position in course """
        return self.annotations[POSITIONKEY]

    def setPositionInCourse(self, position):
        """ Set position in course. """
        self.annotations[POSITIONKEY] = position

    position = property(getPositionInCourse, setPositionInCourse)
            
        
        
        
