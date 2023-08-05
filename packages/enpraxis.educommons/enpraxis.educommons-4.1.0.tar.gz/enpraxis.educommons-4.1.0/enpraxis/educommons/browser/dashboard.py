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
from zope.component import adapts, queryUtility

from zope.app.container.interfaces import INameChooser

from Products.PluggableAuthService.interfaces.authservice import IPropertiedUser

from plone.portlets.interfaces import IPortletManager
from plone.portlets.constants import USER_CATEGORY

from plone.app.portlets.interfaces import IDefaultDashboard
from plone.app.portlets import portlets

from plone.app.portlets.storage import UserPortletAssignmentMapping
    
class DefaultDashboard(object):
    """The default default dashboard.
    """
    
    implements(IDefaultDashboard)
    adapts(IPropertiedUser)
    
    def __init__(self, principal):
        self.principal = principal
    
    def __call__(self):
        return {
            'plone.dashboard1' : (portlets.news.Assignment(), portlets.events.Assignment(),),
            'plone.dashboard2' : (portlets.recent.Assignment(),),
            'plone.dashboard3' : (),
            'plone.dashboard4' : (),
        }
