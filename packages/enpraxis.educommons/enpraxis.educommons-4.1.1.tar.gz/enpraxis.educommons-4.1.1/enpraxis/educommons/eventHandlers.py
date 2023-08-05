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

# eventHandlers.py
from Products.CMFDefault.SyndicationInfo import SyndicationInformation
from collective.zipfiletransport.utilities.interfaces import IZipFileTransportUtility
from enpraxis.educommons.annotations.interfaces import ICourseOrderable, ICourseOrder
from zope.annotation.interfaces import IAnnotations
from zope.app.container.interfaces import IContainerModifiedEvent

from utilities.interfaces import IECUtility
from zope.component import getUtility, queryUtility
import re


RE_BODY = re.compile('<body[^>]*?>(.*)</body>', re.DOTALL )

def syndicateFolderishObject(object, event):
    """ Enable RSS feed upon FolderishObject creation. """
    if not hasattr(object.aq_explicit, 'syndication_information'):
        syInfo = SyndicationInformation()
        object._setObject('syndication_information', syInfo)
        portal = object.portal_url.getPortalObject()
        portal_syn = portal.portal_syndication
        syInfo = object._getOb('syndication_information')
        syInfo.syUpdatePeriod = portal_syn.syUpdatePeriod
        syInfo.syUpdateFrequency = portal_syn.syUpdateFrequency
        syInfo.syUpdateBase = portal_syn.syUpdateBase
        syInfo.max_items = portal_syn.max_items
        syInfo.description = "Channel Description"

def addCoursePosition(object, event):
    """ Add a course position """
    if object.Type() != 'Course':
        if ICourseOrderable.providedBy(object) and not object.isTemporary():
            if object.getExcludeFromNav():
                order = ICourseOrder(object)
                if order.position:
                    order.position = 0
                    object.reindexObject()
            else:
                # assign new position
                order = ICourseOrder(object)
                if not order.position:
                    # If it is not already assigned
                    ecutil = getUtility(IECUtility)
                    parent = ecutil.FindECParent(object)
                    if parent:
                        path = {'path':{'query':'/'.join(parent.getPhysicalPath())+'/',},
                                'getExcludeFromNav':False,}
                        brains = object.portal_catalog.searchResults(path, sort_on='getObjPositionInCourse')
                        if brains:
                            lastobj = brains[-1].getObject()
                            if lastobj.getId() == parent.id + '.zip':
                                # If the last object is the course zip file, trade places
                                lo = ICourseOrder(lastobj)
                                order.position = lo.position
                                lo.position = lo.position + 1
                                lastobj.reindexObject()
                            else:
                                order.position = ICourseOrder(lastobj).position + 1
                        else:
                            order.position = 1
                    object.reindexObject()
        

def addObjPosition(object, event):
        appendObjPosition(object)

def appendObjPosition(object):
    if ICourseOrderable.providedBy(object) and not object.isTemporary():
        order = ICourseOrder(object)
        if 'Course' == object.Type():
            # Course is always the first object in the list
            order.position = 0
        else:
            ecutil = queryUtility(IECUtility)
            if ecutil:
                parent = ecutil.FindECParent(object)
                if 'Course' == parent.Type():
                    if object.getExcludeFromNav():
                        # Course order is not important if excludeFromNav is not set
                        order.position = 0;
                    elif 0 == order.position:
                        # Add to the end
                        path = {'path':{'query':'/'.join(parent.getPhysicalPath())+'/'},
                                'getExcludeFromNav':False,}
                        brains = object.portal_catalog.searchResults(path)
                        pos = []
                        for x in brains:
                            # Courses are unlikely to have too many nav objects, so 
                            # use getObject for now
                            cobj = x.getObject()
                            if ICourseOrderable.providedBy(cobj):
                                border = ICourseOrder(x.getObject())
                                if border:
                                    pos.append(border.position)
                        try:
                            order.position = max(pos) + 1
                        except ValueError:
                            # If no objects are in the list
                            order.position = 1
                        # Append course download to end of list
                        zipobj = getattr(parent, parent.id + '.zip', None)
                        if zipobj:
                            zord = ICourseOrder(zipobj)
                            zord.position = order.position + 1
                            zipobj.reindexObject()
                else:
                    # Object not in course
                    order.position = 0
            else:
                # Could not determine if object is in a course or not
                order.position = 0
                                       

def updateZipDownload(object, event):
    """ Check for factors related to editing and adding objects """
    pw = event.object.portal_workflow

    if pw.getInfoFor(event.object,'review_state') == 'Published':
        validateContext(object, event)

    

def ZipFileMaker(event):
    """ Handler for creating zip download for objects that are moving through workflow changes """

    if event.bulkChange and event.target in ['manager_rework','retract']:
        validateContext(event.object,event)        
    elif event.initial_state == 'Published' or event.target == 'publish':
        validateContext(event.object,event)
    else:
        pass 

def deleteObjectHandler(event):
    """ Handlet the delete object event """
    if event.bulkChange == True:
        if event.contains_published:
            validateContext(event.object, event)
    else:
        validateContext(event.object, event)


def validateContext(object, event):
    """ create the Zipfile after some final checks """

    parent = getUtility(IECUtility).FindECParent(object)
    file_id = parent.id + '.zip'
    pw = event.object.portal_workflow
    
    if parent.portal_type == 'Course':
        if pw.getInfoFor(parent,'review_state') == 'Published':
            if not event.object.isTemporary():
                if event.object.id != file_id:
                    if not IContainerModifiedEvent.providedBy(event):
                        ZipFileCreator(parent,event).createZipFile()


## Deprecated for 3.1.0, as auto generated Course packages have been disabled
## Replaced by Package Course functionality :: browser/packagecourseview.py
class ZipFileCreator:

    def __init__(self, object, event):
        self.obj = object
        self.event = event

    def createZipFile(self):
        """ Create a zip file for when the file is modified. """

        course = self.obj
        file_id = course.id + '.zip'

        pm = course.portal_membership
        user_id = pm.getAuthenticatedMember().id
        roles = pm.getAuthenticatedMember().getRoles()
        if 'Publisher' in roles:
            roles += ['Administrator']
            course.manage_setLocalRoles(user_id, roles)
            course.reindexObjectSecurity()

        data = self.getZipFileData(course=course)

        if not data:
            return

        if not hasattr(course,file_id):
                    
            course.invokeFactory("File",file_id)
            fileobj = getattr(course,file_id)
            fileobj.content_status_modify(workflow_action='submit')
            fileobj.content_status_modify(workflow_action='release')
            fileobj.content_status_modify(workflow_action='publish')
            fileobj.setTitle("Download This Course")

        else:
            fileobj = getattr(course,file_id)            
            fileobj.setTitle("Download This Course")

        
        fileobj.setExcludeFromNav(False)
        fileobj.setFile(data)
        appendObjPosition(fileobj)

        course.portal_catalog.reindexObject(fileobj)
        user_ids = []
        user_ids += [user_id]
        course.manage_delLocalRoles(userids=user_ids)
        course.reindexObjectSecurity()

    def getZipFileData(self, course, obj_paths=[], filename=None):
        """
        Return the content for a zip file
        """
        objects_list = getUtility(IZipFileTransportUtility)._createObjectList(course, obj_paths, state=['Published'])
        objects_list.insert(0,course)
        context_path = str( course.virtual_url_path() )

        # Do not include the zip file for the course
        mod_objects_list = [object for object in objects_list if object.virtual_url_path().replace(course.virtual_url_path(),'') != '/' + course.id + '.zip']
        
        if mod_objects_list:
            content = getUtility(IZipFileTransportUtility)._getAllObjectsData(mod_objects_list, context_path)
            return content
        else:
            return None

