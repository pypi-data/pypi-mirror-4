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
from plone.app.workflow.interfaces import ISharingPageRole
from enpraxis.educommons.browser.interfaces import IeduCommonsSharingPageRole

from enpraxis.educommons import eduCommonsMessageFactory as _

# These are for everyone

class ProducerRole(object):
    implements(IeduCommonsSharingPageRole)
    
    title = _(u"Producer")
    required_permission = None
    
class QARole(object):
    implements(IeduCommonsSharingPageRole)
    
    title = _(u"QA", default=u"QA")
    required_permission = None
    
class PublisherRole(object):
    implements(IeduCommonsSharingPageRole)
    
    title = _(u"Publisher")
    required_permission = None

class ViewerRole(object):
    implements(IeduCommonsSharingPageRole)

    title = _(u"Viewer")
    required_permission = None
