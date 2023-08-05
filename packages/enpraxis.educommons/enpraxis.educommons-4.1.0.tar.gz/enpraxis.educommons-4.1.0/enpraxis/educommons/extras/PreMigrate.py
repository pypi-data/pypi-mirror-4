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

from Products.CMFCore.utils import getToolByName
from StringIO import StringIO
from Products.contentmigration.basemigrator.walker import CatalogWalker 
from Products.contentmigration.basemigrator.migrator import CMFFolderMigrator
from zope.app.annotation.interfaces import IAnnotations, IAttributeAnnotatable
from zope.component import getUtility, getMultiAdapter
from zope.interface import directlyProvidedBy, directlyProvides
from Products.CMFPlone.PloneTool import transaction
from plone.portlets.interfaces import IPortletManager, IPortletAssignmentMapping
from plone.app.redirector.interfaces import IRedirectionStorage
from BeautifulSoup import BeautifulSoup
from Products.CMFPlone.interfaces import IPropertiesTool
from urlparse import urljoin, urlunparse, urlparse
from urllib import unquote
from zope.component import queryUtility
import re

# base class to migrate objects and retain their license annotations
class eduCommonsFoldersMigrator(CMFFolderMigrator):
    """Persist annotations to new object"""

    def migrate_annotations(self):
        """Persist annotations"""
        if hasattr(self.old, '__annotations__'):
            annotations = self.old.__annotations__
            self.new.__annotations__ = annotations
            if self.old.__annotations__.has_key('eduCommons.accessible'):
                self.new.__annotations__['migrate.access'] = self.old.__annotations__['eduCommons.accessible']
            if self.old.__annotations__.has_key('eduCommons.clearcopyright'):
                self.new.__annotations__['migrate.cc'] = self.old.__annotations__['eduCommons.clearcopyright']
            if self.old.__annotations__.has_key('eduCommons.adacompliant'):
                self.new.__annotations__['migrate.ada'] = self.old.__annotations__['eduCommons.adacompliant']
	    if getattr(self.old, 'getEffectiveDate') and self.old.getEffectiveDate():
	        self.new.__annotations__['migrate.effectivedate'] = self.old.getEffectiveDate()
            if getattr(self.old, 'getExpirationDate') and self.old.getExpirationDate():
	        self.new.__annotations__['migrate.expirationdate'] = self.old.getExpirationDate()
        
    def migrate_current_workflow(self):
        """Annotate the current workflow state"""
        wft = self.old.portal_url.portal_workflow
        cur_state = wft.getInfoFor(self.old, 'review_state')
        self.new.__annotations__['review_state'] = cur_state


class CourseMigrator(eduCommonsFoldersMigrator):
    """Base class to migrate to Folder """
    
    def migrate_courseproperties(self):
        """Place course specific fields in an annotation, to be used in 3.1.1 to 3.2.1 migration """

        if hasattr(self.old, 'term'):
            self.new.__annotations__['course.term'] = self.old.term
        if hasattr(self.old, 'courseId'):
            self.new.__annotations__['course.courseid'] = self.old.courseId
        if hasattr(self.old, 'structure'):
            self.new.__annotations__['course.structure'] = self.old.structure            
        if hasattr(self.old, 'level'):
            self.new.__annotations__['course.level'] = self.old.level
        if hasattr(self.old, 'instructorName'):
            self.new.__annotations__['course.instructorname'] = self.old.instructorName
        if hasattr(self.old, 'instructorAsCreator'):
            self.new.__annotations__['course.instructor_principal'] = self.old.instructorAsCreator
        if hasattr(self.old, 'instructorEmail'):
            self.new.__annotations__['course.instructoremail'] = self.old.instructorEmail
        if hasattr(self.old, 'displayInstEmail'):
            self.new.__annotations__['course.displayInstructorEmail'] = self.old.displayInstEmail
        if hasattr(self.old, 'crosslisting'):
            self.new.__annotations__['course.crosslisting'] = self.old.crosslisting            
        if hasattr(self.old, 'getLocation'):
	    self.new.__annotations__['course.location'] = self.old.getLocation()

        #determine if FSS file exists in course#
        portal_url = getToolByName(self.old, 'portal_url')

        fss_file = self.old.portal_catalog(path={'query':'/'.join(self.new.getPhysicalPath()) + '/'}, portal_type='FSSFile', review_state='Published')
        if fss_file:
            self.new.__annotations__['course.hasFSS'] = 1
        
        
        text = self.old.getText()
        self.new.__annotations__['course.text'] = text
        
    def migrate_portlets(self):
        """ Remove the portlets associated with the course """
        rightColumn = getUtility(IPortletManager, name=u'plone.rightcolumn', context=self.new)
        right = getMultiAdapter((self.new, rightColumn), IPortletAssignmentMapping, context=self.new)
        del right['OER Recommender']
        del right['Course Summary']
        del right['Reuse Course']        

    walkerClass = CatalogWalker
    src_meta_type = 'Course'
    src_portal_type = 'Course'
    dst_meta_type = 'ATFolder'
    dst_portal_type = 'Folder'

class DivisionMigrator(eduCommonsFoldersMigrator):
    """Base class to migrate to Folder """

    def migrate_deptproperties(self):
        """Place course specific fields in an annotation, to be used in 3.1.1 to 3.2.1 migration """
        text = self.old.getText()
        self.new.__annotations__['dept.text'] = text


    walkerClass = CatalogWalker
    src_meta_type = 'Division'
    src_portal_type = 'Division'
    dst_meta_type = 'ATFolder'
    dst_portal_type = 'Folder'


def remove_fss_files(self):
    """Removed course download zips"""

    out = StringIO()
    print >> out, "Starting removal process"

    portal_url = getToolByName(self, 'portal_url')
    portal = portal_url.getPortalObject()

    files = portal.portal_catalog(path={'query':'/'.join(portal.getPhysicalPath()) + '/'}, portal_type='FSSFile')
    for file in files:
        obj = file.getObject()
        parent = obj.aq_inner.aq_parent
        parent.manage_delObjects([obj.id,])
    print >> out, "Deleted all objects"

def resolveuid(traverse_subpath, context, request):

    requestpath = ''
    if len(traverse_subpath) > 1 and traverse_subpath[0] == 'resolveuid':
        uuid = traverse_subpath[1]
	if uuid.find('#') != -1:
	    requestpath = '#' + uuid.split('#')[-1]
	    uuid = uuid.split('#')[0]
	elif uuid.find('?') != -1:
	    requestpath = '?' + uuid.split('?')[-1]
	    uuid = uuid.split('?')[0]
    else:
	return '/'.join(traverse_subpath), ''

    reference_tool = getToolByName(context, 'reference_catalog')
    obj = reference_tool.lookupObject(uuid)
    if not obj:
        hook = getattr(context, 'kupu_resolveuid_hook', None)
        if hook:
            obj = hook(uuid)
    if obj:
        portal = obj.portal_url.getPortalObject()
        target = obj.virtual_url_path().replace(portal.virtual_url_path() + '/','')
        return target, requestpath + '/'.join(['',] + traverse_subpath[2:])
    else:
	return '/'.join(traverse_subpath), ''

def resolveAcquisition(url, ruid, val):
    """ This resolves acquisition. Needs to be updated so that it searches through each level of the url and searches for and newpath in each one """
    rpath = ruid[val]
    if rpath[0] == '/':
        ops = rpath.split('/')[1:]
    else:
        ops = rpath.split('/')
    ups = url.split('/')[1:]
    if ops[0] in ups and ops[0] != ups[0]:
        index = ups.index(ops[0])
        path = ['',] + ups[:index] + ops
	searchpath = ''
        storage = getUtility(IRedirectionStorage)
	if path[-1] in ['image_large', 'image_preview', 'image_mini', 'image_thumb', 'image_tile', 'image_icon', 'image_listing', 'document_view']:
            newpath = storage.get(unquote('/'.join(path[:-1])))
	    searchpath = path[-1]
	else:
            newpath = storage.get(unquote('/'.join(path)))
        if newpath:
            relpath = _convertLinkToRelative(newpath,url)
	    if searchpath:
                ruid[val] = relpath + '/' + searchpath
	    else:
                ruid[val] = relpath
            return True

def pre_migrate_3_1_1_to_3_2_1(self):
    """Run the migration"""
     
    out = StringIO()
    print >> out, "Starting migration"
         
    portal_url = getToolByName(self, 'portal_url')
    portal = portal_url.getPortalObject()

    brains = portal.portal_catalog(path={'query':'/'.join(portal.getPhysicalPath()) + '/'},) 
    for brain in brains:
        obj = brain.getObject()
	obj.wl_clearLocks()
        if hasattr(obj.aq_explicit, 'getRawText') and callable(obj.aq_explicit.getRawText):
            text = obj.getRawText()
            soup = BeautifulSoup(text)
            ruids = soup.findAll(src=True)
            ruids += soup.findAll(href=True)
	    textchange = False
	    for ruid in ruids: 
	        if ruid.has_key('src'):
	            val = 'src'
	        elif ruid.has_key('href'):
		    val = 'href'
	 	if ruid[val].find('resolveuid') == 0:
                    attr = ruid[val]
	            textchange = True
                    ruid[val], extras = resolveuid(attr.split('/'), obj, obj.REQUEST)
                    if ruid.has_key('class'):
                        ruid['class'] = '%s resolvethisuid' %(ruid['class'],)
                    else:
                        ruid['class'] = 'resolvethisuid'
		    ruid['extraattrs'] = extras
		elif ruid[val].find('://') == -1:
		    url = brain.getPath()
	            if brain.Type in ['Course','Division'] and url[-1] != '/':
			url += '/'
		    oldpath = urljoin(url,ruid[val])
                    storage = getUtility(IRedirectionStorage)
                    searchpath = ''
		    if oldpath.split('/')[-1] in ['image_large', 'image_preview', 'image_mini', 'image_thumb', 'image_tile', 'image_icon', 'image_listing', 'document_view']:
			newpath = storage.get(unquote('/'.join(oldpath.split('/')[:-1])))
			searchpath = oldpath.split('/')[-1]
		    else:		    
		        newpath = storage.get(unquote(oldpath))
		    if newpath:
		        relpath = _convertLinkToRelative(newpath,url) 
			if searchpath:
                            ruid[val] = relpath + '/' + searchpath
			else:
                            ruid[val] = relpath
	                textchange = True
	            elif len(ruid[val]) != 0:
                        if resolveAcquisition(url, ruid, val):
                            textchange = True
            if textchange:
                obj.setText(soup.renderContents(), mimetype='text/html')

    is_lp_installed = False
    for log in portal.portal_setup.keys():
	if 'import-all-profile-Products.LinguaPlone_LinguaPlone' in log:
            is_lp_installed = True
    if portal.portal_quickinstaller.isProductInstalled('LinguaPlone'):
        is_lp_installed = True

    site_properties = getattr(portal.portal_properties, 'site_properties', None)
    site_properties._updateProperty('enable_link_integrity_checks', False)
                
    #create migrateable_properties to migrate old site props
    if not getattr(portal.portal_properties, 'migrateable_properties', None):
        portal.portal_properties.addPropertySheet('migrateable_properties', 'Old Site Properties')
    m_props = portal.portal_properties.migrateable_properties

    if not getattr(m_props, 'site_title', None):
        m_props.manage_addProperty(id='site_title', type='string', value=portal.title)
        m_props.manage_addProperty(id='description', type='string', value=portal.description)
        m_props.manage_addProperty(id='email_from_address', type='string', value=portal.email_from_address)
        m_props.manage_addProperty(id='email_from_name', type='string', value=portal.email_from_name)
        m_props.manage_addProperty(id='is_lp_installed', type='string', value=is_lp_installed)
	m_props.manage_addProperty(id='webstats_js', type='string', value=portal.portal_properties.site_properties.webstats_js)

    migrators = ( CourseMigrator, DivisionMigrator)
    
    for migrator in migrators:
        walker = migrator.walkerClass(portal, migrator)
        walker.go(out=out)
        transaction.commit()
        print >> out, walker.getOutput()
        
    #Remove all FSS Files
    remove_fss_files(portal)        

    #Refresh catalog indices
    self.portal_catalog.reindexIndex(self.portal_catalog.indexes(),None)

    print >> out, "Migration finished"
    return out.getvalue()

def _convertLinkToRelative(link, current):
    # This will break if the last item in the url path is a folder
    # Make sure you rewrite the link path before you call this function
    hr = urlparse(link)
    c = urlparse(current)
    if c[1] == hr[1]:
        url1 = c[2].split('/')
        url2 = hr[2].split('/')
        index = 0
        while url1[index:] and url2[index:] and url1[index] == url2[index]:
            index += 1
        p = []
        for y in range(len(url1[index+1:])):
            p.append('..')
        p = p + url2[index:]
        return urlunparse(('', '', '/'.join(p), hr[3], hr[4], hr[5]))

