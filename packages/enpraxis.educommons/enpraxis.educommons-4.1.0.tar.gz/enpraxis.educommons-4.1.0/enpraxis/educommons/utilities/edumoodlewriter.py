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
from collective.imstransport.utilities.interfaces import IIMSManifestWriter
from collective.imstransport.utilities.packagingio import ZipfileWriter
from collective.imstransport.utilities.moodle.moodlewriter import MoodleWriter
from collective.imstransport.utilities.imscp.cpresourcewriter import CPResourceWriter
from collective.imstransport.utilities.imsinterchange import IMSWriter
from collective.imstransport import IMSTransportMessageFactory as _
from collective.imstransport.utilities.moodle.imsmoodlewriter import IMSMoodleWriter

class eduMoodleWriter(IMSMoodleWriter):
    """ Write an IMS content package manifest file. """

    def _getObjectPath(self, obj, context):
        """ Get the path of an object. """

        root_path = context.aq_inner.aq_parent.virtual_url_path()
        obj_path = obj.aq_explicit.virtual_url_path()

        if obj_path.find(root_path) != 0:
            return ''

        # Remove the path of the folder object
        path = obj_path.replace(root_path, '')
        if path and path[0] == '/':
            path = path[1:]

        if not path:
            return ''

        if hasattr(obj.aq_explicit, 'Format'):
            from urlparse import urlparse
            if 'text/html' == obj.Format():
                url = urlparse(path)
                if url[2].split('.')[-1] not in ['htm', 'html']:
                    path += '.html'

        return path 


