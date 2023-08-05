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

from xml.dom import minidom
from collective.imstransport.IMS_exceptions import ManifestError

ec_namespace = 'http://cosl.usu.edu/xsd/eduCommonsv1.2'

class eduMetadata(object):
    """ Read eduCommons metadata """

    def __init__(self):
        """ Initialize self.document objects """
        self.document = minidom.Document()

    def readEduMetadata(self, metadata, md):
        """ Read custom metadata """
        ecn = metadata.getElementsByTagNameNS(ec_namespace, 'eduCommons')
        if ecn:
            objectType_nodes = ecn[0].getElementsByTagName('objectType')
            if objectType_nodes:
                ot = self.getTextValue(objectType_nodes[0])
                if ot:
                    if ot not in ['Course', 'Large File', 'Document', 'File', 'Image', 'Link']:
                        raise ManifestError, '"%s" is not a recognized object type.' %ot
                    md['type'] = '%s' %ot
            copyright_nodes = ecn[0].getElementsByTagName('copyright')
            if copyright_nodes:
                cn = self.getTextValue(copyright_nodes[0])
                if cn:
                    md['rights'] = cn
            license_nodes = ecn[0].getElementsByTagName('license')
            if license_nodes:
                license_node = license_nodes[0]
                license = [str(license_node.getAttribute('category'))]
                licenseName_nodes = license_node.getElementsByTagName('licenseName')
                if licenseName_nodes:
                    license.append(str(self.getTextValue(licenseName_nodes[0])))
                else:
                    license.append('None')
                licenseUrl_nodes = license_node.getElementsByTagName('licenseUrl')
                if licenseUrl_nodes:
                    license.append(str(self.getTextValue(licenseUrl_nodes[0])))
                else:
                    license.append('None')
                licenseIconUrl_nodes = license_node.getElementsByTagName('licenseIconUrl')
                if licenseIconUrl_nodes:
                    license.append(str(self.getTextValue(licenseIconUrl_nodes[0])))
                else:
                    license.append('None')
                md['license'] = license
            clearedCopyright_nodes = ecn[0].getElementsByTagName('clearedCopyright')
            if clearedCopyright_nodes:
                cc = self.getTextValue(clearedCopyright_nodes[0])
                if 'true' == cc:
                    md['clearedCopyright'] = True
                else:
                    md['clearedCopyright'] = False
            accessibility_nodes = ecn[0].getElementsByTagName('accessible')
            if accessibility_nodes:
                access = self.getTextValue(accessibility_nodes[0])
                if 'true' == access:
                    md['accessible'] = True
                else:
                    md['accessible'] = False
            courseId_nodes = ecn[0].getElementsByTagName('courseId')
            if courseId_nodes:
                cin = self.getTextValue(courseId_nodes[0])
                if cin:
                    md['courseId'] = cin
            term_nodes = ecn[0].getElementsByTagName('term')
            if term_nodes:
                tm = self.getTextValue(term_nodes[0])
                if tm:
                    md['term'] = tm
            displayInsEmail_nodes = ecn[0].getElementsByTagName('displayInstructorEmail')
            if displayInsEmail_nodes:
                die = self.getTextValue(displayInsEmail_nodes[0])
                if 'true' == die:
                    md['displayInstEmail'] = True
                else:
                    md['displayInstEmail'] = False
            instrIsPrincipal_nodes = ecn[0].getElementsByTagName('instructorAsPrincipalCreator')
            if instrIsPrincipal_nodes:
                iis = self.getTextValue(instrIsPrincipal_nodes[0])
                if 'true' == iis:
                    md['instructorAsCreator'] = True
                else:
                    md['instructorAsCreator'] = False

    def writeEduMetadata(self, md, type, copyright, linfo, clearcopyright, accessible, courseid = '', term = '', displayinstemail='false', instascreator='false'):
        """ Write custom metadata """
        ecn = self._createNode(md, '', 'eduCommons', attrs=[('xmlns', ec_namespace)])
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
        
    def getTextValue(self, node):
        """ Removes the text from the text_node of a node """
        for x in node.childNodes:
            if x.nodeType == x.TEXT_NODE:
                return x.nodeValue.strip()
        return None

    def _createNode(self, parent, nspace, ename, value=None, attrs=None):
        """ Create a node in the document. """
        newnode = self.document.createElementNS(nspace, ename)
        if nspace:
            newnode.setAttribute('xmlns', nspace)
        parent.appendChild(newnode)
        if value and value != '':
            if not isinstance(value, unicode):
                newnode.appendChild(self.document.createTextNode(value.decode('utf-8')))
            else:
                newnode.appendChild(self.document.createTextNode(value))
        if attrs:
            for x in attrs:
                newnode.setAttribute(x[0], x[1])
        return newnode
