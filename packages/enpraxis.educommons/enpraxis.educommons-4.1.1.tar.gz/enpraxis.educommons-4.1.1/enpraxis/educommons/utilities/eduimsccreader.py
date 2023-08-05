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

from zope.component import getUtility
from collective.imstransport.utilities.interfaces import IIMSObjectCreator
from collective.imstransport.utilities.imsinterchange import IMSReader
from collective.imstransport.utilities.packagingio import ZipfileReader
from collective.imstransport.utilities.imscc.ccreader import CCReader
from collective.imstransport.IMS_exceptions import ManifestError
from collective.imstransport.utilities.imscc.configcc import LOM_CC_namespace
from xml.parsers.expat import ExpatError
from edumetadata import eduMetadata
import re
from zipfile import BadZipfile

class eduCCReader(CCReader):
    """ Read eduCommons CC metadata """

    def readCustomMetadata(self, resource, md):
        """ Reading custom metadata """
        metadata_nodes = resource.getElementsByTagName('metadata')
        if metadata_nodes:
            lom_nodes = metadata_nodes[0].getElementsByTagNameNS(LOM_CC_namespace, 'lom')
            if lom_nodes:
                edumetadata = eduMetadata()
                edumetadata.readEduMetadata(lom_nodes[0], md)        
                mmd_nodes = lom_nodes[0].getElementsByTagName('metaMetadata')
                if mmd_nodes:
                    id_nodes = mmd_nodes[0].getElementsByTagName('identifier')
                    if id_nodes:
                        entry_nodes = id_nodes[0].getElementsByTagName('entry')
                        if entry_nodes:
                            md['id'] = self.getTextValue(entry_nodes[0]).encode('ascii')

        

class eduIMSCCReaderUtility(IMSReader):
    """ Create objects from IMS manifest. """

    def readPackage(self, file, context):
        """ Read the manifest """
        try:
            source = ZipfileReader(file)
        except BadZipfile:
             raise ManifestError, 'Internal error. No source object specified'
        objDict = {}
        educcreader = eduCCReader()
        manifest = source.readManifest()
        if not manifest:
            return False, \
                   'Manifest', \
                   'Could not locate manifest file "imsmanifest.xml" in the zip archive.'
        try:
            doc = educcreader.parseManifest(manifest)
        except ExpatError, e:
            raise ManifestError, str(e)
        objDict['package'] = {}
        educcreader.readPackageMetadata(doc, objDict['package'])
        orgs = educcreader.readOrganizations(doc)
        resources = educcreader.readResources(doc)
        for x in resources:
            resid, restype, reshref = educcreader.readResourceAttributes(x)
            metadata = educcreader.readMetadata(x)
            files = educcreader.readFiles(x)
            defaultmetadata = metadata.copy()
            educcreader.readCustomMetadata(x, metadata)
            # determine if eduCommons metadata has been added
            ecmeta = len(metadata) - len(defaultmetadata)
            # If the type is a link
            if restype == 'imswl_xmlv1p0':
                for y in files:
                    hash = resid + y
                    objDict[hash] = metadata
                    id = self.createIdFromFile(y)
                    objDict[hash]['id'] = id.replace('.xml','')
                    objDict[hash]['path'] = self.createCoursePathFromFile(y, ecmeta)
                    linkfile = source.readFile(y)
                    title, location = educcreader.getLinkInfo(linkfile)
                    objDict[hash]['type'] = 'Link'
                    objDict[hash]['title'] = title
                    objDict[hash]['remoteUrl'] = location
            # If the type is a file
            elif restype == 'webcontent':
                for y in files:
                    hash = resid + y
                    if metadata.has_key('type') and metadata['type'] == 'Course':
                        objDict['package'] = metadata
                        objDict['package']['file'] = y
                        objDict['package']['position'] = 0
                        objDict['package']['excludeFromNav'] = False
                        if orgs.has_key(resid):
                            if not (objDict['package'].has_key('title') and objDict['package']['title']):
                                objDict['package']['title'] = orgs[resid][1]
                    # If there is only one file, or it matches the reshref
                    # add the metadata to it if it exists
                    elif y == reshref or len(files) == 1:
                        objDict[hash] = metadata
                        # If it is listed in the org section
                        if orgs.has_key(resid):
                            objDict[hash]['position'] = orgs[resid][0]
                            objDict[hash]['excludeFromNav'] = False
                            # Use 'and' as opposed to 'or' to avoid KeyError
                            if not (objDict[hash].has_key('title') and objDict[hash]['title']):
                                objDict[hash]['title'] = orgs[resid][1]
                        else:
                            objDict[hash]['excludeFromNav'] = True
                        objDict[hash]['file'] = y
                        objDict[hash]['type'] = self.determineType(objDict[hash], y)
                        if not objDict[hash].has_key('id'):
                            objDict[hash]['id'] = self.createIdFromFile(y)

                        if not (objDict[hash].has_key('title') and objDict[hash]['title']):
                            objDict[hash]['title'] = objDict[hash]['id']
                        objDict[hash]['path'] = self.createCoursePathFromFile(y, ecmeta) 
                    # If it is just a lowly file
                    else:
                        objDict[hash] = {}
                        objDict[hash]['excludeFromNav'] = True
                        objDict[hash]['file'] = y
                        objDict[hash]['type'] = self.determineType(objDict[hash], y)
                        objDict[hash]['id'] = self.createIdFromFile(y)
                        objDict[hash]['path'] = self.createCoursePathFromFile(y, ecmeta) 

        objcreator = getUtility(IIMSObjectCreator)
        objcreator.createObjects(objDict, context, source)

    def createCoursePathFromFile(self, file, incourse):
        """ Get folder path from file path """
        if incourse:
            return '/'.join(file.split('/')[1:-1])
        else:
            return '/'.join(file.split('/')[:-1])

        

      
