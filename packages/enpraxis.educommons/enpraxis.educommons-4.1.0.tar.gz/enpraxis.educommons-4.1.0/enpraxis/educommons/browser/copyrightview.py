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

from zope.publisher.browser import BrowserView
from enpraxis.educommons.annotations.interfaces import IClearCopyrightable, IClearCopyright
from enpraxis.educommons import eduCommonsMessageFactory as _


class CopyrightView(BrowserView):
    """ Provides view of object with access to annotations in placeless environments"""

    def changeCopyright(self, value):
        """ Provides annotation to placeless script """
        message = ''        
        if IClearCopyrightable.providedBy(self.context):
            clear = IClearCopyright(self.context)
            if 'True' == value and not clear.clearedcopyright:
                clear.clearedcopyright = True
                message = _(u'Copyright Cleared')
                self.context.reindexObject()
            elif 'False' == value and clear.clearedcopyright:
                clear.clearedcopyright = False
                message = _(u'Copyright Revoked')
                self.context.reindexObject()
        return message


