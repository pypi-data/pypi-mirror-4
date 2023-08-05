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
from zope.component import getUtility
from zope.annotation.interfaces import IAnnotations
from collective.contentlicensing.browser import RSSView as DefaultRSSView
from Products.CMFPlone.utils import getToolByName
from enpraxis.educommons.utilities.interfaces import IECUtility
from enpraxis.educommons.annotations.interfaces import ICourseOrderable, ICourseOrder
from collective.contentlicensing.utilities.interfaces import IContentLicensingUtility
from Products.Five.formlib.formbase import EditForm
from urlparse import urlsplit
from xml.dom import minidom
from string import split, find
import urllib
from Acquisition import aq_base, aq_inner, aq_parent


class ClearCopyrightField(BrowserView):
    """ Render the additional cleared copyright field in the edit form  """
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def getClearedCopyright(self):
        """ Get the clear copyright value from the object  """
        annotations = IAnnotations(self.context)
	if annotations.has_key('eduCommons.clearcopyright'):
            return annotations['eduCommons.clearcopyright']
        else:
	    return

class ChangeCopyrightForm(BrowserView):
    """ Test  """
    def __init__(self, context, request):
        self.context = context
        self.request = request

class AccessibilityCompliantField(BrowserView):
    """ Render the additional accessibility compliant field in the edit form  """
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def getAccessibilityCompliant(self):
        """ Get the Accessibility Compliant value from the object  """
        annotations = IAnnotations(self.context)
	if annotations.has_key('eduCommons.accessible'):
            return annotations['eduCommons.accessible']
        else:
	    return

class ChangeAccessibleCompliantForm(BrowserView):
    """ Test  """
    def __init__(self, context, request):
        self.context = context
        self.request = request


class SkinlessView(BrowserView):
    """ Render a view without the CMS chrome  """

    def getSkinlessView(self):
        """ Set Titles based on type and get body  """
       
        if self.context.Type() in ['Page', 'School', 'Division']:
            title = self.context.Title()
            content = self.context.getText()
        else:
            #Get Full Course Title
            portal_catalog = self.context.portal_catalog
            brain = portal_catalog(id=self.context.id)[0]
            self.ecutil = getUtility(IECUtility)
            title = self.ecutil.getFullCourseTitle(brain)
            content = self.context.getText()

        return title, content

class DivisionListingView(BrowserView):
    """ Return Division in the School """

    def getDivisions(self):
        """ Get Sorted Divisions  """

        portal_catalog = self.context.portal_catalog
        brains = portal_catalog(path= {'query':'/'.join(self.context.getPhysicalPath())+'/', 'depth':2}, portal_type='Division')

        #brains = list(brains)
        #brains.sort(lambda x, y : cmp(self.ecutil.getFullCourseTitle(x),self.ecutil.getFullCourseTitle(y)))

        return brains


class SortedCourseListingView(BrowserView):
    """ Return Courses in the Dept sorted by full course name  """

    def getSortedCourses(self):
        """ Get Sorted Courses  """
    
        self.ecutil = getUtility(IECUtility)
        portal_catalog = self.context.portal_catalog
        brains = portal_catalog(path= {'query':'/'.join(self.context.getPhysicalPath())+'/', 'depth':2}, 
                                portal_type='Course', 
                                sort_on="getFullCourseName")
        #brains = list(brains)
        #brains.sort(lambda x, y : cmp(self.ecutil.getFullCourseTitle(x),self.ecutil.getFullCourseTitle(y)))

        return brains

class SortedCrossCourseListingView(BrowserView):
    """ Return Cross listed Courses in the Dept sorted by full course name  """

    def getSortedCrossCourses(self):
        """ Get Sorted Cross Listed Courses  """
    
        self.ecutil = getUtility(IECUtility)
        brains = self.context.reference_catalog.searchResults(relationship='crosslisted-in',
                                                              targetId=self.context.getId())
        uids = [x.sourceUID for x in brains]
        ccourses = self.context.portal_catalog.searchResults(UID=uids, sort_on="getFullCourseName")
        return ccourses

class SortedResourceListingView(BrowserView):
    """ Return Non-Course objects in the Dept sorted by name  """

    def getSortedResources(self):
        """ Get Sorted Resources  """
        resources = []
        brains = self.context.getFolderContents()
        for brain in brains:
            if 'Course' != brain.portal_type and brain.getObject().getExcludeFromNav() == False:
                resources += [brain]
            
        resources = list(resources)

        resources.sort(lambda x, y : cmp(x.id, y.id))

        return resources


class RSSView(DefaultRSSView):
    """ Implements eduCommons RSS view """

    def getRSSObjects(self):
        """ Get RSS objects. """
        if self.context.Type() in ['School', 'Division', 'Course']:
            syn = self.context.portal_syndication
            objs = list(syn.getSyndicatableContent(self.context))
            objs.reverse()

        else:
            objs = self.context.portal_catalog.searchResults(portal_type='Course',
                                                             sort_on='modified',
                                                             sort_order='reverse')
        return objs
        
    def isPartOf(self, obj):
        """ Gets the parent object of course materials via FindECParent or returns parent object """
                
        self.ecutil = getUtility(IECUtility)
        parent = self.ecutil.FindECParent(obj)
        parentType = parent.Type()
        if parentType == 'Course' and obj.Type() != 'Course':
            return parent.Type(), parent.absolute_url()
        elif parentType == 'Course' and obj.Type() == 'Course':
            return parent.Type(), obj.aq_parent.absolute_url()            
        elif obj.Type() != 'Plone Site':
            return obj.aq_parent.Type(), obj.aq_parent.absolute_url()
        else:
            return ['','']
        


def unicode_sanitize(text):
    """
    Intended to be used to correct the inconsistency of plone when you call
    methods such as Title or Publisher which should ALLWAYS return a unicode
    object if the output is text.
    """
    if isinstance(text,list):
        sanit_list = []
        for item in text:
            if isinstance(item, str):
                sanit_list += item.decode('utf-8')
            else:
                sanit_list += item
        text = sanit_list          
    elif isinstance(text, str):
        text = text.decode('utf-8')
    return text


class CopyrightBylineView(BrowserView):
    """ Implements eduCommons Citation view for customized Creator information """

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.props = self.context.portal_url.portal_properties.content_licensing_properties
        self.clutil = getUtility(IContentLicensingUtility)
        self.ecutil = getUtility(IECUtility)

    def getLicenseByline(self):
        """ Get the license byline fields for an object. """

        copyright = self.context.Rights()
        if not copyright:
            copyright = self.props.DefaultSiteCopyright
        holder, license = self.clutil.getLicenseAndHolderFromObject(self.context)
        if '(site default)' == holder:
            holder = self.props.DefaultSiteCopyrightHolder
        if 'Site Default' == license[0]:
            license = self.props.DefaultSiteLicense
        license_name = license[1]
        if not license_name or 'None' == license_name:
            license_name = ''
        if 'Creative Commons License' == license[0]:
            license_name = license[0]
        license_url = license[2]
        if not license_url or 'None' == license_url:
            license_url = ''
        license_button = license[3]
        if not license_button or 'None' == license_button:
            license_button = ''
        return copyright, holder, license_name, license_url, license_button

    def getCitationInfo(self):
        """ Gets the citation information """

        # Title
        title = self.context.title
        title = title.replace('--', '-')

        # Creators
        creator = '' 
        index = 1

        parent = self.ecutil.FindECParent(self.context)
        parentType = parent.Type()
        names = []
        if '(course_default)' in self.context.Creators() and parentType == 'Course':
            if parent.instructorAsCreator == True:
                instr_name = parent.instructorName
                if instr_name != u'':
                    names = [instr_name.strip()]
                names += [name.strip() for name in parent.Creators()]
                if len(self.context.Creators()) > 1:
                    names += [name.strip() for name in self.context.Creators()[1:]]
        elif self.context.Type() == 'Course':
            if self.context.instructorAsCreator == True:
                instr_name = self.context.instructorName
                if instr_name != u'':
                    names = [instr_name.strip()]
            names += [name.strip() for name in self.context.Creators()]
        else:
            names += [name.strip() for name in self.context.Creators()]
            
        for cr in names:
            inits = ''
            crs = []

            crs = cr.split(' ')

            for part in crs[:-1]:
                inits += ' ' + part[0] + '.'   
        
            creator += crs[-1]
            if inits:
                creator += "," + inits
            creator += ', '
            index += 1
            
        if creator:
            creator = creator[:-2]
            if creator:
                if creator[-1] != '.':
                    creator += '.'
         
        id = self.context.getId()
        
        portal_url = getToolByName(self.context, 'portal_url')
        portal_name = portal_url.getPortalObject().title
        
        create_date = self.context.creation_date.strftime('%Y, %B %d')
        
          
        url = self.context.absolute_url()

        import datetime
        date = datetime.date.today().strftime('%B %d, %Y')
 
        
        if creator:
            prompt_text = "%s (%s). %s. Retrieved %s, from %s Web site: %s." %(unicode_sanitize(creator),create_date,unicode_sanitize(title),date,unicode_sanitize(portal_name),url)
        else:
            prompt_text = "%s. (%s). Retrieved %s, from %s Web site: %s." %(unicode_sanitize(title),create_date,date,unicode_sanitize(portal_name),url)

        return prompt_text.replace('\'','\\\'').replace('\"','\\\'')
  



class RDFMetadataView(BrowserView):
    """ Express Dublin Core As Rdf  """

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.document = minidom.Document()
        self.clutil = getUtility(IContentLicensingUtility)
        self.ecutil = getUtility(IECUtility)
        self.props = self.context.portal_url.portal_properties.content_licensing_properties
        self.holder, self.license = self.clutil.getLicenseAndHolderFromObject(context)

    def __call__(self):
        self.request.response.setHeader('Content-Type', 'application/rdf+xml')
        return self.writeRDF()

    def writeRDF(self):
        """ Write RDF metadata """
        parent = self.ecutil.FindECParent(self.context)
        if 'Creative Commons License' == self.license[0] or ('Creative Commons License' == self.props.DefaultSiteLicense[0] and 'Site Default' == self.license[0]):
            if self.license[0] == 'Site Default':
                self.license = self.props.DefaultSiteLicense
            data = self.getCCLicenseRDF(parent)
        else:
            data = self.getRDFMetadata(parent)
        # Remove the XML header
        index = find(data, '\n')
        if (index > -1):
            data = data[index + 1:]
	return data

    def getRDFMetadata(self, parent):
        """ Write metadata fields as RDF. """
        rdf_node = self._createNode(self.document, 'rdf:RDF',
                       attrs=[('xmlns:rdf', 'http://www.w3.org/1999/02/22-rdf-syntax-ns#'),
                              ('xmlns:dc', 'http://purl.org/dc/elements/1.1/'),
                              ('xmlns:dcterms', 'http://purl.org/dc/terms')])
        desc_node = self._createNode(rdf_node, 'rdf:Description',
                        attrs=[('rdf:about', self.context.renderBase())])
        self._writeDCMetadata(desc_node, parent)
        return self.document.toprettyxml()        
                                

    def getCCLicenseRDF(self, parent):
        """ Write into RDF CC License elements. """
        holder, license = self.clutil.getLicenseAndHolderFromObject(self.context)
        licenseId = ''
        if len(self.license) >= 3:
            lid = urlsplit(self.license[2])
            if len(lid) >= 3:
                lid = lid[2].split('/')
                if len(lid) >= 3:
                    licenseId = lid[2]

        if licenseId and self.clutil.hasCCLicenseInfo(licenseId):

            cc_rdf = self.clutil.getCCLicenseInfo(licenseId)
        
            rdf_node = self._createNode(self.document, 'rdf:RDF',
                           attrs=[('xmlns', 'http://web.resource.org/cc/'),
                                  ('xmlns:dc', 'http://purl.org/dc/elements/1.1/'),
                                  ('xmlns:rdf', 'http://www.w3.org/1999/02/22-rdf-syntax-ns#'),
                                  ('xmlns:ec', 'http://educommons.com/xsd/coursemetadata1.0.rdf#')])
            work_node = self._createNode(rdf_node, 'Work', attrs=[('rdf:about',
                                                                   self.context.renderBase())])
            self._writeDCMetadata(work_node, parent)
            
            parent = self.ecutil.FindECParent(self.context)
            parentType = parent.Type()
            if parentType == 'Course':
                self._writeCourseMetadata(work_node, parent)
                self._createNode(work_node, 'license', attrs=[('rdf:resource', self.license[2])])
            return self.document.toprettyxml()
        else:
            return ''

    def _writeCourseMetadata(self, node, parent):
        """ Write the Course metadata in RDF. """

        # Course ID
        if parent.getCourseId() != '':
            self._createNode(node, 'ec:course_id', parent.getCourseId())

        # Course Term
        if parent.getTerm() != '':
            self._createNode(node, 'ec:term', parent.getTerm())

        # Course Structure
        if parent.getStructure() != '':
            self._createNode(node, 'ec:structure', parent.getStructure())

        # Course Level
        if parent.getLevel() != '':
            self._createNode(node, 'ec:level', parent.getLevel())


    def _writeDCMetadata(self, node, parent):
        """ Write the dublin core metadata in RDF. """

        # Identifier
        self._createNode(node, 'dc:identifier', self.context.renderBase())

        # Title
        self._createNode(node, 'dc:title', self.context.Title())

        # Language
        lang = self.context.Language()
        if not lang:
            po = self.context.portal_url.getPortalObject()
            lang = po.portal_properties.site_properties.getProperty('default_language')
        self._createNode(node, 'dc:language', lang) 

        # Description
        desc = self.context.Description()
        if desc:
            self._createNode(node, 'dc:description', self.context.Description()) 

        # Subject
        self._renderList(node, 'dc:subject', self.context.Subject())

        # Type
        self._createNode(node, 'dc:type', self.context.Type()) 

        #Creators
        parent = self.ecutil.FindECParent(self.context)
        parentType = parent.Type()
        course_creators = []
        creators = self.getFilteredCreators(self.context)

        if '(course_default)' in creators and parentType == 'Course':
            if parent.instructorAsCreator == True:
                cres = parent.instructorName
                course_creators = [cres]
            for creator in self.getFilteredCreators(parent):
                course_creators.append(creator)
            if len(creators) > 1:
                course_creators += creators[1:]
        elif self.context.Type() == 'Course':
            if self.context.instructorAsCreator == True:
                cres = self.context.instructorName
                course_creators = [cres]
            for creator in creators:
                course_creators.append(creator)
        else:
            course_creators = creators
        if course_creators:
            self._renderList(node, 'dc:creator', course_creators)


        # Contributors
        self._renderList(node, 'dc:contributor', self.context.Contributors())

        # Publisher
        self._createNode(node, 'dc:publisher', self.context.portal_url.getPortalObject().Publisher()) 

        # Format
        self._createNode(node, 'dc:format', self.context.Format()) 

        # Rights
        rights = self.context.Rights()
        if not rights:
            rights = self.props.DefaultSiteCopyright
        self._createNode(node, 'dc:rights', rights) 

    def getFilteredCreators(self, context):
        creators = context.Creators()
        filteredlist = []
        for x in creators:
            if x and '@' == x[0]:
                filteredlist.append(x[1:])
            else:
                filteredlist.append(x)
        return filteredlist

    def _renderList(self, node, element, value):
        """ Render a list of items in RDF. """
        if value:
            if len(value) > 1:
                value_node = self._createNode(node, element)
                bag_node = self._createNode(value_node, 'rdf:Bag')
                for x in value:
                    self._createNode(bag_node, 'rdf:li', x)
            else:
                self._createNode(node, element, value[0])
        

    def _createNode(self, parent, ename, value=None, attrs=None):
        """ Create a node in the document. """
        newNode = self.document.createElement(ename)
        parent.appendChild(newNode)
        if value:
            value = value.replace('--','-')
            newNode.appendChild(self.document.createTextNode(unicode_sanitize(value)))
        if attrs:
            for x in attrs:
                newNode.setAttribute(x[0], unicode_sanitize(x[1]))
        return newNode




        
