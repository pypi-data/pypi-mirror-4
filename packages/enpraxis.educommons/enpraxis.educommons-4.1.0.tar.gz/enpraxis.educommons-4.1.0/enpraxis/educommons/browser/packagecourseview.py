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
from Products.CMFPlone import PloneMessageFactory as _
from Products.CMFPlone.utils import _createObjectByType
from zope.component import getUtility, queryUtility
from collective.zipfiletransport.utilities.interfaces import IZipFileTransportUtility
from zope.annotation.interfaces import IAnnotations
from enpraxis.educommons.utilities.interfaces import IECUtility
from enpraxis.educommons.annotations.interfaces import ICourseOrder
from Products.CMFCore.utils import getToolByName
from collective.imstransport.utilities.interfaces import IIMSTransportUtility
from zope.event import notify
from zope.lifecycleevent import ObjectModifiedEvent


class PackageCourseView(BrowserView):
    """View to package a published course """

    def __call__(self):
        self.createIMSFile()
        message = _('Course has been packaged')
        url = '%s/folder_contents' % self.context.absolute_url()
        self.context.plone_utils.addPortalMessage(message)
        self.request.response.redirect(url)

    def createIMSFile(self):
        """ Create a downloadable version of the course in IMS format """
        course = self.context
        file_id = course.id + '.zip'
        ims_util = getUtility(IIMSTransportUtility)
        data, course = ims_util.exportPackage(course, file_id, packagetype='IMS Common Cartridge')
        if file_id in course.objectIds():
            dcobj = getattr(course, file_id)
            dcobj.setFile(data)
            dcobj.setFilename(file_id)
        else:
            title = _(u'Download this Course')
            _createObjectByType('File', course, id=file_id, title=title)
            dcobj = getattr(course, file_id)
            dcobj.setFile(data)
            dcobj.setContentType('application/zip')
            dcobj.setFilename(file_id)
            dcobj.setExcludeFromNav(True)
            wftool = getToolByName(dcobj, 'portal_workflow')
            wftool.doActionFor(dcobj, 'submit')
            wftool.doActionFor(dcobj, 'release')
            wftool.doActionFor(dcobj, 'publish')        
        notify(ObjectModifiedEvent(dcobj))


