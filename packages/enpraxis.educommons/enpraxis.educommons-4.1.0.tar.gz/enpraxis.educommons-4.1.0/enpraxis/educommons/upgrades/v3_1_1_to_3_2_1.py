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

from HTMLParser import HTMLParseError
from Products.CMFPlone.utils import _createObjectByType
from Products.CMFCore.WorkflowCore import WorkflowException
from StringIO import StringIO
import string
import re
from zope.component import getUtility, getMultiAdapter
from Products.CMFCore.utils import getToolByName
from enpraxis.educommons import portlet
from collective.imstransport.utilities.interfaces import IIMSTransportUtility
from plone.portlets.interfaces import IPortletManager, IPortletAssignmentMapping
from BeautifulSoup import BeautifulSoup

def migrate(portal_setup):
    """ Migration from eduCommons 3.1.1 to 3.2.1  """
    out = StringIO()
    print >> out, '<h3>Starting Migration</h3>\n'
    print >> out, '<ul>\n'
    
    self = portal_setup
    
    portal_url = getToolByName(portal_setup, 'portal_url')
    portal=  portal_url.getPortalObject()    
    
    oldsite = getattr(portal.aq_parent, 'eduCommons')
    
    deleteDefaultContent(self, portal, out)
    copyZMIObjects(self, portal, oldsite, out)
    copyFolders(self, portal, oldsite, out)
    migrateTheme(self, portal, oldsite, out)
    migrateProperties(self, portal, oldsite, out)
    migrateUsers(self, portal, oldsite, out)
    updateAdmins(self, portal, oldsite, out)
    updateBaseProperties(self, portal, oldsite, out)
    replaceuid(self, portal)
    #deleteOldSite(self, portal, oldsite, out)

def replaceuid(self, portal):
    """ replaceall the uid entries """

    brains = portal.portal_catalog(path={'query':'/'.join(portal.getPhysicalPath()) + '/'},Language="all") 
    for brain in brains:
        obj = brain.getObject()
        if hasattr(obj, 'getRawText') and callable(obj.getRawText):
            text = obj.getRawText()
	    try:
                soup = BeautifulSoup(text)
	    except HTMLParseError:
		continue
            ruids = soup.findAll(attrs={'class':re.compile('resolvethisuid$')})
            for ruid in ruids:
                if ruid.has_key('src'):
                    src = ruid['src']
		    qobj = portal.portal_catalog(path={'query':'%s/%s' %(portal.id, src)},)
		    if qobj:
		        srcval = 'resolveuid/%s' %(qobj[0].UID)	
		        if ruid.has_key('extraattrs') and ruid['extraattrs']:
		            srcval = srcval + ruid['extraattrs']
			ruid['src'] = srcval
                else:
                    href = ruid['href']
		    qobj = portal.portal_catalog(path={'query':'%s/%s' %(portal.id, href)},)
		    if qobj:
		        hrefval = 'resolveuid/%s' %(qobj[0].UID)	
		        if ruid.has_key('extraattrs') and ruid['extraattrs']:
		            hrefval = hrefval + '/' + ruid['extraattrs']
			ruid['href'] = hrefval
	    obj.setText(soup.renderContents(), mimetype='text/html') 

def deleteDefaultContent(self, portal, out):
    """ Remove default objects """
    portal.manage_delObjects(['about', 'help', 'front-page'])    
    print >> out, '<li>Deleted default content</li>\n'

def copyZMIObjects(self, portal, oldsite, out):
    """ Copies old objects to new instace """
    portal.MailHost = oldsite.MailHost    
    portal.portal_skins.custom = oldsite.portal_skins.custom
    
def copyFolders(self, portal, oldsite, out):
    """ Copies the top level folders from oldsite to portal """    

    folders = oldsite.portal_catalog.searchResults(Type='Folder', 
                                                 path={'query':'/',
                                                       'depth':2,})
    print >> out, '  <li>Copying Folders</li>\n'
    print >> out, '  <ul>\n'

    for folder in folders:
        obj = folder.getObject()
        if obj.__annotations__.has_key('dept.text'):
            migrateDivision(self, portal, oldsite, obj)
        else:
            co = oldsite.manage_copyObjects(obj.id)        
            portal.manage_pasteObjects(co)
            setWorkflow(self, getattr(portal, obj.id), obj)
            if obj.portal_workflow.getInfoFor(obj, 'review_state'):
                wf = obj.portal_workflow
                review_state = wf.getInfoFor(obj, 'review_state')
                moveWorkflow(self, getattr(portal, obj.id), review_state)
                obj.workflow_history = getattr(portal, obj.id).workflow_history

        print >> out, '    <li>Copied %s</li>\n' %obj.Title()                    
    print >> out, '  </ul>\n'
    print >> out, '  <li>Copied Content</li>\n'
    
    # Migrate other top level content

    objs = oldsite.portal_catalog.searchResults(portal_type=['File', 'Image', 'Document'],
                                                path={'query':'/',
                                                      'depth':2,})
    obj_ids = [x.id for x in objs]
    co = oldsite.manage_copyObjects(obj_ids)
    portal.manage_pasteObjects(co)
    for x in obj_ids:
        obj = getattr(oldsite, x)
        newobj = getattr(portal, x)
        if x != 'front-page':
            newobj.setExcludeFromNav(True)
        if obj.__annotations__.has_key('review_state'):
            moveWorkflow(self, newobj, obj.__annotations__['review_state'])
    
    
    
def migrateTheme(self, portal, oldsite, out):
    """ Delete default base_properties in portal and migrate oldsite base_properties  """    
    if getattr(oldsite.portal_skins.custom, 'base_properties', None):
        old_custom = oldsite.portal_skins.custom
        new_custom = portal.portal_skins.custom        
        new_custom.base_properties = old_custom.base_properties        
        
        print >> out, '  <li>Migrated theme</li>\n'
        
        
def migrateProperties(self, portal, oldsite, out):
    """ Transfer old properties to new  """        
    #Migrate eduCommons Properties
    old_ec_props = oldsite.portal_properties.educommons_properties
    new_ec_props = portal.portal_properties.educommons_properties
    for prop in old_ec_props.propertyMap():
        #Overwrite default new values with default old values
        if prop['id'] in new_ec_props.propertyIds():
            id = prop['id']
            key_value = {id : old_ec_props.getProperty(id) }
            new_ec_props.manage_changeProperties(**key_value)
        #Add properties if they don't exist in new
        else:
            id = prop['id']
            type = prop['type']
            value = old_ec_props.getProperty(id)
            new_ec_props.manage_addProperty(id=id, type=type, value=value)
            
    print >> out, '  <li>Migrated eduCommons Properties</li>\n'

    #Migrate ContentLicensing Propertiese
    old_cl_props = oldsite.portal_properties.content_licensing_properties
    new_cl_props = portal.portal_properties.content_licensing_properties
    for prop in old_cl_props.propertyMap():
        #Overwrite default new values with default old values
        if prop['id'] in new_cl_props.propertyIds():
            id = prop['id']
            if id != 'Jurisdiction':
                key_value = {id : old_cl_props.getProperty(id) }
                new_cl_props.manage_changeProperties(**key_value)
            else:
                for value in new_cl_props.jurisdiction_options:
                    if old_cl_props.getProperty(id) in value:
                        new_cl_props.manage_changeProperties(Jurisdiction=value)
        #Add properties if they don't exist in new
        else:
            id = prop['id']
            type = prop['type']
            value = old_cl_props.getProperty(id)
            new_cl_props.manage_addProperty(id=id, type=type, value=value)
            
    print >> out, '  <li>Migrated ContentLicensing Properties</li>\n'

    #Migrate relevant old site properties
    old_site_props = oldsite.portal_properties.migrateable_properties
    portal.manage_changeProperties(title=old_site_props.site_title,
                                    description=old_site_props.description,
                                    email_from_address=old_site_props.email_from_address,
                                    email_from_name=old_site_props.email_from_name
                                    )
    portal.portal_properties.site_properties.manage_changeProperties(webstats_js=old_site_props.webstats_js)  
    print >> out, '  <li>Migrated Site properties</li>\n'


        
def migrateUsers(self, portal, oldsite, out):
    """ Migrate Users """
    old_users = oldsite.acl_users.manage_copyObjects(['local_roles', 
                                                      'mutable_properties', 
                                                      'portal_role_manager',
                                                      'source_groups', 
                                                      'source_users'])
    portal.acl_users.manage_delObjects(['local_roles', 
                                         'mutable_properties', 
                                         'portal_role_manager',
                                         'source_groups', 
                                         'source_users'])
    portal.acl_users.manage_pasteObjects(old_users)

    #Activate plugins for each copied object
    acl_users = portal.acl_users
    acl_users.local_roles.manage_activateInterfaces(['ILocalRolesPlugin',
                                                     'IRolesPlugin'])
    acl_users.mutable_properties.manage_activateInterfaces(['IPropertiesPlugin',
                                                            'IUserEnumerationPlugin'])
    acl_users.portal_role_manager.manage_activateInterfaces(['IRoleAssignerPlugin',
                                                             'IRoleEnumerationPlugin',
                                                             'IRolesPlugin'])
    acl_users.source_groups.manage_activateInterfaces(['IGroupEnumerationPlugin',
                                                       'IGroupIntrospection',
                                                       'IGroupManagement',
                                                       'IGroupsPlugin'])
    acl_users.source_users.manage_activateInterfaces(['IAuthenticationPlugin', 
                                                      'IUserAdderPlugin', 
                                                      'IUserEnumerationPlugin', 
                                                      'IUserIntrospection', 
                                                      'IUserManagement'])

    old_pgd = oldsite.portal_groupdata
    portal.portal_groupdata = old_pgd

    old_pmd = oldsite.portal_memberdata
    portal.portal_memberdata = old_pmd

    #Set all users default editor to Kupu
    users = portal.acl_users.getUsers()
    for user in users:
        user.setProperties(wysiwyg_editor = 'Kupu')

    print >> out, '  <li>Migrated Users</li>\n'
        

def updateAdmins(self, portal, oldsite, out):
    """ Convert users that have administrator role to have manager role """
    users = portal.acl_users.getUsers()
    for user in users:
        roles = user.getRoles()
        index = 0
        update = 0
        for role in roles:            
            if role == 'Administrator':
                roles[index] = 'Manager'
                update = 1                
            index += 1
        if update == 1:
            portal.acl_users.userFolderEditUser(user.getId(), None, roles, user.getDomains())
        
def updateBaseProperties(self, portal, oldsite, out):
    """ Update logo.gif to logo.png to  """        
    custom = portal.portal_skins.custom.aq_inner.aq_explicit
    if hasattr(custom, 'base_properties'):
        base_props = custom.base_properties
        if base_props.plone_skin == 'Left Skin':
            if base_props.logoName == 'logo.gif':
                base_props.manage_changeProperties(logoName='logo.png')
                                
def publishObject(context):
    """ Move an object into the published state """
    wftool =  getToolByName(context, 'portal_workflow')

    if wftool.getInfoFor(context, 'review_state') != 'Published':
        wftool.doActionFor(context, 'submit')
        wftool.doActionFor(context, 'release')
        wftool.doActionFor(context, 'publish')        


def migrateDivision(self, portal, oldsite, dobj):
    """ Migrate a division from the old site to the new. """
    # Create a new division
    _createObjectByType('Division',
                        portal,
                        id=dobj.getId(),
                        title=dobj.Title(),
                        description=dobj.Description(),
                        subject=dobj.Subject(),
                        contributors=dobj.Contributors(),
                        creators=dobj.Creators(),
                        rights=dobj.Rights(),
                        creation_date=dobj.CreationDate(),
                        )
    # Copy over remaining division attributes
    div = getattr(portal, dobj.getId())
    div.setText(dobj.__annotations__['dept.text'])
    old_site_props = oldsite.portal_properties.migrateable_properties
    clpinst = str(old_site_props.is_lp_installed)
    if clpinst == 'True':
        course.setLanguage(cobj.Language())
    #div.syndication_information = dobj.syndication_information
    for x in dobj.__annotations__.keys():
        if 'review_state' == x:
            moveWorkflow(self, div, dobj.__annotations__[x])
        if x != 'dept.text':
            div.__annotations__[x] = dobj.__annotations__[x]
        elif 'migrate.cc' == x:
            div.__annotations__['eduCommons.clearcopyright'] = dobj.__annotations__[x]
        elif 'migrate.access' == x:
            div.__annotations__['eduCommons.accessiblilty'] = dobj.__annotations__[x]
        elif 'migrate.ada' == x:
            div.__annotations__['eduCommons.adacompliant'] = dobj.__annotations__[x]
	elif 'migrate.effectivedate' == x:
	    div.setEffectiveDate(dobj.__annotations__[x])
	elif 'migrate.expirationdate' == x:
	    div.setExpirationDate(dobj.__annotations__[x])

    # Copy Course sub objects
    oc = []
    for oid,obj in dobj.objectItems():
        if 'Folder' == obj.Type():
            ann = getattr(obj, '__annotations__', None)
            if ann and ann.has_key('course.text'):
                migrateCourse(self, div, oldsite, obj)
            elif oid != 'syndication_information':
                oc.append(oid)
        else:
            oc.append(oid)

    # Copy all other sub objects
    co = dobj.manage_copyObjects(oc)
    div.manage_pasteObjects(co)

    for oid,obj in div.objectItems():
        if 'Course' != obj.Type() and 'syndication_information' != oid:
	    if getattr(dobj, oid).__annotations__.has_key('review_state'):
                moveWorkflow(self, obj, getattr(dobj, oid).__annotations__['review_state'])
                obj.workflow_history = getattr(dobj, oid).workflow_history
            elif dobj.portal_workflow.getInfoFor(getattr(dobj, oid), 'review_state'):
	        wf = dobj.portal_workflow
	        review_state = wf.getInfoFor(getattr(dobj, oid), 'review_state')
                moveWorkflow(self, obj, review_state)
                obj.workflow_history = getattr(dobj, oid).workflow_history
    div.reindexObject()

def migrateCourse(self, div, oldsite, cobj):
    """ Migrate a course from the old site to the new. """

    # Create a new course
    _createObjectByType('Course',
                        div,
                        id=cobj.getId(),
                        )

    # Copy over remaining course attributes
    course = getattr(div, cobj.getId())
    course.setDescription(cobj.Description())
    course.setTitle(cobj.Title())
    course.setSubject(cobj.Subject())
    course.setContributors(cobj.Contributors())
    course.setCreators(cobj.Creators())
    old_site_props = oldsite.portal_properties.migrateable_properties
    clpinst = str(old_site_props.is_lp_installed)
    if clpinst == 'True':
        course.setLanguage(cobj.Language())
    course.setRights(cobj.Rights())
    course.setCreationDate(cobj.CreationDate())

    course.setText(cobj.__annotations__['course.text'])
    course.setLocation(cobj.__annotations__['course.location']) 
    a2f = {'course.term':'term',
           'course.courseid':'courseId',
           'course.instructorname':'instructorName',
           'course.instructor_principal':'instructorAsCreator',
           'course.instructoremail':'instructorEmail',
           'course.displayInstructorEmail':'displayInstEmail',
           'course.structure':'structure',
           'course.level':'level',
           'course.crosslisting':'crosslisting'}
    for x in cobj.__annotations__.keys():
        if x in a2f:
            mut = course.getField(a2f[x]).getMutator(course)
            mut(cobj.__annotations__[x])
        elif 'review_state' == x:
            moveWorkflow(self, course, cobj.__annotations__[x])
        elif 'migrate.cc' == x:
            course.__annotations__['eduCommons.clearcopyright'] = cobj.__annotations__[x]
        elif 'migrate.access' == x:
            course.__annotations__['eduCommons.accessiblilty'] = cobj.__annotations__[x]
        elif 'migrate.ada' == x:
            course.__annotations__['eduCommons.adacompliant'] = cobj.__annotations__[x]
	elif 'migrate.effectivedate' == x:
	    course.setEffectiveDate(cobj.__annotations__[x])
	elif 'migrate.expirationdate' == x:
	    course.setExpirationDate(cobj.__annotations__[x])
        else:
            course.__annotations__[x] = cobj.__annotations__[x]

    #ensure course has 0 position
    course.__annotations__['eduCommons.objPositionInCourse'] = 0    

    #ensure portlets exist on courses
    rightColumn = getUtility(IPortletManager, name=u'plone.rightcolumn', context=course)
    right = getMultiAdapter((course, rightColumn), IPortletAssignmentMapping, context=course)

    #This code breaks the course object when the server has no outbound access to the web
    if u'OER Recommender' not in right:
        right[u'OER Recommender'] = portlet.oerrecommenderportlet.Assignment()

    if u'Course Summary' not in right:
        right[u'Course Summary'] = portlet.courseinfoportlet.Assignment()

    if u'Reuse Course' not in right:
        right[u'Reuse Course'] = portlet.reusecourseportlet.Assignment()

    # Copy Course Objects
    ids = cobj.objectIds()    

    if 'syndication_information' in ids:
        ids.remove('syndication_information')

    # don't copy course download
    zip = cobj.getId() + '.zip'
    if zip in ids:
        ids.remove(zip)
    
    co = cobj.manage_copyObjects(ids)

    course.manage_pasteObjects(co)

    #ensure each object has correct position in course
    for oid in ids:
        olditem = getattr(cobj, oid)
        if olditem.__annotations__.has_key('eduCommons.objPositionInCourse'):
            pos = olditem.__annotations__['eduCommons.objPositionInCourse']
            newitem = getattr(course, oid)
            newitem.__annotations__['eduCommons.objPositionInCourse'] = pos
	if clpinst == 'False':
	    newitem = getattr(course, oid)
            newitem.setLanguage(olditem.portal_languages.getDefaultLanguage())

    setWorkflow(self, course, cobj)
    #If the course package existed, set annotation
    if cobj.__annotations__.has_key('course.hasFSS') and cobj.__annotations__['course.hasFSS'] == 1:
        course.__annotations__['course.hasFSS'] = 1
    course.reindexObject()

def setWorkflow(self, new, old, omappings={}, retainHistory=True):
    for oldid,olditem in old.objectItems():
        zip = new.id + '.zip'
        if oldid in omappings:
            oldid = omappings[oldid]
        if oldid != zip:
            newitem = getattr(new.aq_explicit, oldid)
            try:
                if olditem.portal_workflow.getInfoFor(olditem, 'review_state') != '':
                    state = olditem.portal_workflow.getInfoFor(olditem, 'review_state')
                    moveWorkflow(self, newitem, state)
                    if retainHistory:
                        newitem.workflow_history = olditem.workflow_history
                    if 'Folder' == olditem.Type():
                        setWorkflow(self, newitem, olditem)
                elif olditem.__annotations__.has_key('review_state'):
                    moveWorkflow(self, newitem, olditem.__annotations__['review_state'])
                    if retainHistory:
                        newitem.workflow_history = olditem.workflow_history
                    if 'Folder' == olditem.Type():
                        setWorkflow(self, newitem, olditem)
            except AttributeError:
                pass
            except WorkflowException:
                pass


def moveWorkflow(self, newobj, ostate):
    wt = newobj.portal_workflow
    nstate = wt.getInfoFor(newobj, 'review_state')
    result = False
    if 'Visible' == ostate:
        ostate = 'Published'
    if nstate == ostate:
        result = True
        return result
    elif 'InProgress' == nstate:
        wt.doActionFor(newobj, 'submit', comment='', include_subfolders=False)
        result = moveWorkflow(self, newobj, ostate)
    elif 'QA' == nstate:
        wt.doActionFor(newobj, 'release', comment='', include_subfolders=False)
        result = moveWorkflow(self, newobj, ostate)
    elif 'Released' == nstate:
        wt.doActionFor(newobj, 'publish', comment='', include_subfolders=False)
        result = moveWorkflow(self, newobj, ostate)
    elif 'Published' == nstate:
        result = True
    return result



