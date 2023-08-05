from StringIO import StringIO
from zope.component import getUtility, getMultiAdapter
from Products.CMFCore.utils import getToolByName
from enpraxis.educommons.browser.packagecourseview import appendObjPosition
from collective.imstransport.utilities.interfaces import IIMSTransportUtility

def repackage(self):
    """Run the migration"""
    
    out = StringIO()
    print >> out, "Starting removal process"
    
    portal_url = getToolByName(self, 'portal_url')
    portal = portal_url.getPortalObject()

    coursebrains = portal.portal_catalog(path={'query':'/'.join(portal.getPhysicalPath()) + '/'}, portal_type='Course')
    for coursebrain in coursebrains:
        course = coursebrain.getObject()
        if course.__annotations__.has_key('course.hasFSS') and course.__annotations__['course.hasFSS'] == 1:
            repackageCourse(course)
    print >> out, "Repackaged all courses"

def repackageCourse(course):
    """ Convert existent zipped course downloads to new Common Cartridge based package  """
    file_id = course.id + '.zip'

    ims_util = getUtility(IIMSTransportUtility)
    data, course = ims_util.exportPackage(course, file_id, packagetype='IMS Common Cartridge')

    course.invokeFactory("FSSFile",id=file_id, title="Download this Course")
    fileobj = getattr(course,file_id)
    publishObject(fileobj)
    fileobj.setTitle("Download This Course")

    fileobj.setFile(data)
    fileobj.setExcludeFromNav(True)
    appendObjPosition(fileobj)

    course.portal_catalog.reindexObject(fileobj)


def publishObject(context):
    """ Move an object into the published state """
    wftool =  getToolByName(context, 'portal_workflow')

    if wftool.getInfoFor(context, 'review_state') != 'Published':
        wftool.doActionFor(context, 'submit')
        wftool.doActionFor(context, 'release')
        wftool.doActionFor(context, 'publish')

