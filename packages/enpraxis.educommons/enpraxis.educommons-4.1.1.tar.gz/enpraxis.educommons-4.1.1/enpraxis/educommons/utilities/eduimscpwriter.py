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

from collective.imstransport.utilities.packagingio import ZipfileWriter
from collective.imstransport.utilities.imscp.cpwriter import CPWriter
from zope.component import getUtility
from zope.annotation.interfaces import IAnnotations
from collective.contentlicensing.utilities.interfaces import IContentLicensingUtility
from collective.imstransport.IMS_exceptions import ManifestError
from xml.dom import minidom
from collective.imstransport.utilities.imscp.cpwriter import CPWriter
from collective.imstransport.utilities.imscp.imscpwriter import IMSCPWriter
from collective.imstransport.utilities.imscp.configcp import LOM_version, IMS_schema, IMS_version

LOM_ec_namespace = 'http://cosl.usu.edu/xsd/eduCommonsv1.2'

namespaces = [('xmlns', 'http://www.imsglobal.org/xsd/imscp_v1p1'),
              ('xmlns:imscpmd', 'http://www.imsglobal.org/xsd/imsmd_v1p2'),
              ('xmlns:educommons','http://cosl.usu.edu/xsd/eduCommonsv1.2'),
              ('xmlns:xsi', 'http://www.w3.org/2001/XMLSchema-instance'),]

schema_locations = ['http://cosl.usu.edu/xsd/eduCommonsv1.2 http://cosl.usu.edu/xsd/eduCommonsv1.2.xsd',
                    'http://www.imsglobal.org/xsd/imscp_v1p1 http://www.imsglobal.org/xsd/imscp_v1p2.xsd',
                    'http://www.imsglobal.org/xsd/imsmd_v1p2 http://www.imsglobal.org/xsd/imsmd_v1p2p4.xsd']

class eduCPWriter(CPWriter):

    def createManifest(self, id, ver):
        """ Create a new empty manifest. """
        doc = minidom.Document()
        manifest = self._createNode(doc, '', 'manifest', 
                         attrs=[('identifier', id),
                                ('xmlns:version', ver),])
        self.addNamespaces(manifest, namespaces)
        self.addSchemaLocations(manifest, schema_locations)
        return doc

    def writeEduMetadataNode(self, md, type, copyright, linfo, clearcopyright, accessible, courseid = '', term = '', displayinstemail='false', instascreator='false'):
        """ writing custom educommons data """
        ecn = self._createNode(md, '', 'eduCommons', attrs=[('xmlns', LOM_ec_namespace)])
        if 'Page' == type:
            type = 'Document'
        self._createNode(ecn, '', 'objectType', type)
        if copyright:
            self._createNode(ecn, '', 'copyright', copyright)
        if linfo and linfo[1]:
            license = linfo[1]
            license_node = self._createNode(ecn, '', 'license', attrs=[('category', license[0])])
            if license[1] and license[1] != 'None':
                self._createNode(license_node, '', 'licenseName', license[1])
            if license[2] and license[2] != 'None':
                self._createNode(license_node, '', 'licenseUrl', license[2])
            if license[3] and license[3] != 'None':
                self._createNode(license_node, '', 'licenseIconUrl', license[3])
        self._createNode(ecn, '', 'clearedCopyright', clearcopyright)
        self._createNode(ecn, '', 'accessible', accessible)
        if 'Course' == type:
           if courseid:
              self._createNode(ecn, '', 'courseId', courseid)
           if term:
              self._createNode(ecn, '', 'term', term)
           self._createNode(ecn, '', 'displayInstructorEmail', displayinstemail)
           self._createNode(ecn, '', 'instructorAsPrincipalCreator', instascreator)


    def getMetadataNode(self, resource):
       """ Return the metadata element of a resource """
       metadata_nodes = resource.getElementsByTagName('metadata')
       if metadata_nodes:
          return metadata_nodes[0]
       else:
          return None

class eduIMSCPWriter(IMSCPWriter):
    """ Write an IMS content package manifest file. """

    def createPackage(self, filename, context):
        """ Creates an IMS Package """

        destination = ZipfileWriter(context, file)

        cpw = eduCPWriter()

        # Create the Manifest
        manId = self._createPathId(context.virtual_url_path(), 'MAN')
        manVer = context.ModificationDate()
        doc = cpw.createManifest(manId, manVer)

        # Add top level metadata
        lang = context.Language()
        if not lang:
            lang = context.portal_properties.site_properties.getProperty('default_language')
        cpw.writeTopLevelMetadata(doc,
                                  context.getId(),
                                  context.Title(),
                                  context.portal_url(),
                                  lang,
                                  context.Description(),
                                  context.Subject())

        # Write Organizations and Resources
        orgId = self._createPathId(context.virtual_url_path(), 'ORG')
        orgs = cpw.createOrganizations(doc, orgId)
        res = cpw.createResources(doc)

        if orgs and res:
            objs = self._getAllObjects(context)
            for obj in objs:
                # Need to consider excluding folders
                # Get resource info
                path = self._getObjectPath(obj, context)
                vpath = obj.virtual_url_path()
                refid = self._createPathId(vpath, 'RES')
                # Check if we need to add to the organizations section
                if not obj.getExcludeFromNav():
                    itemId = self._createPathId(vpath, 'ITM')
                    cpw.writeItem(orgs, itemId, refid, obj.title)
                rn = cpw.writeResource(res, refid, obj.Type(), path)

                id = obj.getId()
                title = obj.Title()
                urlbase = obj.portal_url.getPortalObject().renderBase()
                lang = obj.Language()
                if not lang:
                    lang = obj.portal_properties.site_properties.getProperty('default_language')
                desc = obj.Description()
                kw = obj.Subject()
                creators = obj.Creators() 
                contrib = obj.Contributors()
                mod = obj.ModificationDate()
                email = obj.portal_url.getPortalObject().getProperty('email_from_address')
                format = obj.Format()
                size = self.getObjSize(obj)
                location = obj.renderBase()
                value = 'yes'
                rights_holder = obj.portal_properties.site_properties.getProperty('rights_holder')
                rights_holder_email = obj.portal_properties.site_properties.getProperty('rights_holder_email')
                copyright = self._getCopyrightString(obj.Rights(), rights_holder, rights_holder_email)
                
                md = cpw.createResourceMetadata(rn)
                cpw.writeGeneralNode(md, id, title, 'en', desc, kw)
                cpw.writeLifeCycleNode(md, creators, contrib, mod, None)
                cpw.writeMetaMetadataNode(md, id, urlbase, email, mod, None, contrib)
                cpw.writeTechnicalNode(md, format, size, location)
                cpw.writeRightsNode(md, value, copyright, None)

                metadata = cpw.getMetadataNode(rn)

                type = obj.Type()
                copyright = obj.Rights()
                cltool = getUtility(IContentLicensingUtility)
                linfo = cltool.getLicenseAndHolderFromObject(obj)
                if IAnnotations(obj).has_key('eduCommons.clearcopyright') and IAnnotations(obj)['eduCommons.clearcopyright']:
                   clearcopyright = 'true'
                else:
                   clearcopyright = 'false'
                if IAnnotations(obj).has_key('eduCommons.accessible') and IAnnotations(obj)['eduCommons.accessible']:
                   accessible = 'true'
                else:
                   accessible = 'false'

                if type == 'Course':
                   courseid = obj.getCourseId()
                   term = obj.getTerm()
                   if obj.getDisplayInstEmail():
                      displayinstemail = 'true'
                   else:
                      displayinstemail = 'false'
                   if obj.getInstructorAsCreator():
                      instascreator = 'true'
                   else:
                      instascreator = 'false'
                   cpw.writeEduMetadataNode(metadata, type, copyright, linfo, clearcopyright, accessible, courseid, term, displayinstemail, instascreator)
                   cpath = '%s%s' %(id, '.html')
                   self._writeObjectData(obj, cpath, destination)
                   cpw.writeResourceFile(rn, cpath)
                elif type  == 'Link':
                   cpw.writeEduMetadataNode(metadata, type, copyright, linfo, clearcopyright, accessible)
                   link = cpw.getLinkXml(title, obj.getRemoteUrl())
                   rpath = '%s' %path
                   self._writeObjectData(link, rpath, destination)
                   cpw.writeResourceFile(rn, rpath)
                else:
                   cpw.writeEduMetadataNode(metadata, type, copyright, linfo, clearcopyright, accessible)
                   self._writeObjectData(obj, path, destination)
                   cpw.writeResourceFile(rn, path)
                    
        self._writeObjectData(cpw.getManifest(doc), 'imsmanifest.xml', destination)

        if destination:
            return destination.getOutput()
        else:
            return None, None
        
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
