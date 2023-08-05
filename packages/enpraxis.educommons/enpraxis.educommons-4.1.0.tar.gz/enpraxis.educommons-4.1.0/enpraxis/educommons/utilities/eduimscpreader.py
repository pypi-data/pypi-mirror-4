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
from collective.imstransport.utilities.interfaces import IIMSManifestReader
from zope.component import getUtility
from collective.imstransport.utilities.interfaces import IIMSObjectCreator
from collective.imstransport.utilities.imscp.imscpreader import IMSCPReader
from collective.imstransport.utilities.imscp.cpresourcereader import CPResourceReader
from collective.imstransport.utilities.imscp.cpreader import CPReader
from collective.imstransport.utilities.packagingio import ZipfileReader
from collective.imstransport.IMS_exceptions import ManifestError
from edumetadata import eduMetadata
from BeautifulSoup import BeautifulSoup
import re
from zipfile import BadZipfile

class eduCPReader(CPReader):
    """ Customize read custom data method in ResourceReader object """

    def readCustomMetadata(self, resource, md):
        metadata_nodes = resource.getElementsByTagName('metadata')
        if metadata_nodes:
            edumetadata = eduMetadata()
            edumetadata.readEduMetadata(metadata_nodes[0], md)        

class eduIMSCPReader(IMSCPReader):
    """ Create objects from IMS manifest. """

    def readPackage(self, file, context):
        """ Read the manifest """
        try:
            source = ZipfileReader(file)
        except BadZipfile:
             raise ManifestError, 'Internal error. No source object specified'
        objDict = {}
        educpreader = eduCPReader()      
        manifest = source.readManifest()
        if not manifest:
            return False, \
                   'Manifest', \
                   'Could not locate manifest file "imsmanifest.xml" in the zip archive.'

        try:
            doc = educpreader.parseManifest(manifest)
        except ExpatError, e:
            raise ManifestError, str(e)
        objDict['package'] = educpreader.readPackageMetadata(doc)
        orgs = educpreader.readOrganizations(doc)
        resources = educpreader.readResources(doc)

        for x in resources:
            resid, restype, reshref = educpreader.readResourceAttributes(x)
            metadata = educpreader.readMetadata(x)
            files = educpreader.readFiles(x)
            defaultmetadata = metadata.copy()
            educpreader.readCustomMetadata(x, metadata)
            ecmeta = len(metadata) - len(defaultmetadata)

            # If the type is a file
            if metadata.has_key('type') and metadata['type'] ==  'Link':
                for y in files:
                    hash = resid + y
                    objDict[hash] = metadata
                    objDict[hash]['id'] = self.createIdFromFile(y)
                    objDict[hash]['path'] = self.createCoursePathFromFile(y, ecmeta)
                    linkfile = source.readFile(y)
                    title, location = self.getLinkInfo(linkfile)
                    objDict[hash]['type'] = 'Link'
                    objDict[hash]['title'] = title
                    objDict[hash]['remoteUrl'] = location
            elif restype == 'webcontent':
                if not files and reshref:
                    files = [reshref,]
                for y in files:
                    hash = resid + y
                    # If there is only one file, or it matches the reshref
                    # add the metadata to it if it exists
                    if metadata.has_key('type') and metadata['type'] == 'Course':
                        hash = 'package'
                        objDict['package'] = metadata
                        objDict['package']['file'] = y
                        objDict['package']['position'] = 0
                        objDict['package']['excludeFromNav'] = False
                        if orgs.has_key(resid):
                            if not (objDict['package'].has_key('title') and objDict['package']['title']):
                                objDict['package']['title'] = orgs[resid][1]
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
                    # If it is just a lowly file
                    else:
                        objDict[hash] = {}
                        objDict[hash]['excludeFromNav'] = True
                        objDict[hash]['file'] = y
                        objDict[hash]['type'] = self.determineType(objDict[hash], y)
                    # Add to all files
                    id = self.createIdFromFile(y)
                    objDict[hash]['id'] = id
                    if not (objDict[hash].has_key('title') and objDict[hash]['title']):
                        objDict[hash]['title'] = id
                    objDict[hash]['path'] = self.createCoursePathFromFile(y, ecmeta)

        objcreator = getUtility(IIMSObjectCreator)
        objcreator.createObjects(objDict, context, source)

    def createCoursePathFromFile(self, file, incourse):
        """ Get folder path from file path """
        if incourse:
            return '/'.join(file.split('/')[1:-1])
        else:
            return '/'.join(file.split('/')[:-1])

    def getLinkInfo(self, linkfile):
        """ Get the link and title from anchor tag """
        soup = BeautifulSoup(linkfile)
        anchor = soup.find('a')
        href = anchor['href']
        label = anchor.string
        return label, href
        
