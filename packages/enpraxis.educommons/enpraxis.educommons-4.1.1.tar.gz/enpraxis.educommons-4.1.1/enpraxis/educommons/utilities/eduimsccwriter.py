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
from collective.imstransport.utilities.imscc.ccwriter import CCWriter
from zope.component import getUtility
from zope.annotation.interfaces import IAnnotations
from collective.contentlicensing.utilities.interfaces import IContentLicensingUtility
from collective.imstransport.IMS_exceptions import ManifestError
from xml.dom import minidom
from collective.imstransport.utilities.imscc.ccwriter import CCWriter
from collective.imstransport.utilities.imscc.imsccwriter import IMSCCWriter
from collective.imstransport.utilities.imscc.configcc import LOM_namespace, LOM_version, IMS_schema, IMS_version
from edumetadata import eduMetadata

namespaces = [('xmlns', 'http://www.imsglobal.org/xsd/imscc/imscp_v1p1'),
              ('xmlns:lomimscc','http://ltsc.ieee.org/xsd/imscc/LOM'),
              ('xmlns:lom','http://ltsc.ieee.org/xsd/LOM'),
              ('xmlns:educommons','http://cosl.usu.edu/xsd/eduCommonsv1.2'),
              ('xmlns:xsi', 'http://www.w3.org/2001/XMLSchema-instance'),]

schema_locations = ['http://cosl.usu.edu/xsd/eduCommonsv1.2 http://cosl.usu.edu/xsd/eduCommonsv1.2.xsd',
   'http://www.imsglobal.org/xsd/imscc/imscp_v1p1 http://www.imsglobal.org/profile/cc/ccv1p0/derived_schema/imscp_v1p2_localised.xsd',
   'http://ltsc.ieee.org/xsd/LOM http://www.imsglobal.org/profile/cc/ccv1p0/derived_schema/domainProfile_2/lomLoose_localised.xsd',
   'http://ltsc.ieee.org/xsd/imscc/LOM http://www.imsglobal.org/profile/cc/ccv1p0/derived_schema/domainProfile_1/lomLoose_localised.xsd',]

ec_namespace = 'http://cosl.usu.edu/xsd/eduCommonsv1.2'

class eduCCWriter(CCWriter):

    def createManifest(self, id, ver):
        """ Create a new empty manifest. """
        doc = minidom.Document()
        manifest = self._createNode(doc, '', 'manifest', 
                         attrs=[('identifier', id),
                                ('xmlns:version', ver),])
        self.addNamespaces(manifest, namespaces)
        self.addSchemaLocations(manifest, schema_locations)
        return doc

    def writeCustomMetadata(self, md, type, copyright, linfo, clearcopyright, accessible, courseid = '', term = '', displayinstemail='false', instascreator='false'):
        """ Writing custom metadata """
        edumetadata = eduMetadata()
        if md:
            edumetadata.writeEduMetadata(md, type, copyright, linfo, clearcopyright, accessible, courseid, term, displayinstemail, instascreator)

class eduIMSCCWriterUtility(IMSCCWriter):
    """ Write an IMS content package manifest file. """

    def createPackage(self, file, context):
        """ Creates an IMS Package """

        destination = ZipfileWriter(context, file)

        educcwriter = eduCCWriter()

        # Create the Manifest
        manId = self._createPathId(context.virtual_url_path(), 'MAN')
        manVer = context.ModificationDate()
        doc = educcwriter.createManifest(manId, manVer)

        # Add top level metadata
        lang = context.Language()
        if not lang:
            lang = context.portal_properties.site_properties.getProperty('default_language')
        educcwriter.writeTopLevelMetadata(doc,
                                  context.getId(),
                                  context.Title(),
                                  context.portal_url(),
                                  lang,
                                  context.Description(),
                                  context.Subject())

        # Write Organizations and Resources
        orgId = self._createPathId(context.virtual_url_path(), 'ORG')
        itemId = self._createPathId(context.virtual_url_path(), 'SHL')
        orgs = educcwriter.createOrganizations(doc, orgId, itemId)
        res = educcwriter.createResources(doc)

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
                    educcwriter.writeItem(orgs, itemId, refid, obj.title)
                rn = educcwriter.writeResource(res, refid, obj.Type(), path)

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
                mod = obj.ModificationDate().replace(' ','T')
                email = obj.portal_url.getPortalObject().getProperty('email_from_address')
                format = obj.Format()
                size = self.getObjSize(obj)
                location = obj.renderBase()
                value = 'yes'
                rights_holder = obj.portal_properties.site_properties.getProperty('rights_holder')
                rights_holder_email = obj.portal_properties.site_properties.getProperty('rights_holder_email')
                copyright = self._getCopyrightString(obj.Rights(), rights_holder, rights_holder_email)
                
                md = educcwriter.createResourceMetadata(rn)
                educcwriter.writeGeneralNode(md, id, title, urlbase, lang, desc, kw)
                educcwriter.writeLifeCycleNode(md, creators, contrib, mod, lang)
                educcwriter.writeMetaMetadataNode(md, id, urlbase, email, mod, lang, contrib)
                educcwriter.writeTechnicalNode(md, format, size, location)
                educcwriter.writeRightsNode(md, value, copyright, lang)

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


                if 'Course' == type:
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
                   educcwriter.writeCustomMetadata(md, type, copyright, linfo, clearcopyright, accessible, courseid, term, displayinstemail, instascreator)
                   cpath = '%s%s' %(id, '.html')
                   self._writeObjectData(obj, cpath, destination)
                   educcwriter.writeResourceFile(rn, cpath)
                elif type == 'Link': 
                   link = educcwriter.getLinkXml(title, obj.getRemoteUrl())
                   rpath = '%s%s' %(path,'.xml')
                   educcwriter.writeCustomMetadata(md, type, copyright, linfo, clearcopyright, accessible)
                   self._writeObjectData(link, rpath, destination)
                   educcwriter.writeResourceFile(rn, rpath)
                else:
                   educcwriter.writeCustomMetadata(md, type, copyright, linfo, clearcopyright, accessible)
                   self._writeObjectData(obj, path, destination)
                   educcwriter.writeResourceFile(rn, path)

        self._writeObjectData(educcwriter.getManifest(doc), 'imsmanifest.xml', destination)

        if destination:
            return destination.getOutput()
        else:
            return None, None

    def _getObjectPath(self, obj, context):
        """ Get the path of an object. """
        
        root_path = context.aq_inner.aq_parent.virtual_url_path()
        obj_path = obj.aq_explicit.virtual_url_path()

        # If a file or image, write the actual file name in path
        if obj.Type() in ['File', 'Image']:
            obj_path = '/'.join(obj_path.split('/')[:-1] + [obj.getFilename()])

        if obj_path.find(root_path) != 0:
            return ''

        # Remove the path of the folder object
        path = obj_path.replace(root_path, '')
        if path and path[0] == '/':
            path = path[1:]

        if not path:
            return ''

        if hasattr(obj.aq_explicit, 'Format'):
            if 'text/html' == obj.Format() and obj.isPrincipiaFolderish:
                path += '.html'

        return path


        
        
        
