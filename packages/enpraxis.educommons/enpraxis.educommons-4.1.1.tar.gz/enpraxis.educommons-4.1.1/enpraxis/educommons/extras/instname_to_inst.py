# This script is an external method to mass copy the InstructorName field
# To the new InstitutionName field. It can be run as follows.
#
#     1. Copy this file to the parts/zope2/Extensions directory in your 
#        eduCommons install
#
#     2. Launch your eduCommons instance
#
#     3. Navigate to the ZMI and find the root of your eduCommons site
#
#     4. Add a new external method with the following parameters:
#         Id: instname_to_inst
#         Title: instname_to_inst
#         Module Name: instname_to_inst
#         Function Name: instname_to_inst
#        and then save your changes.
#
#    5. Click on the new external method and run it by clicking on the
#       "test" tab. This script will take a long time to run if you have a 
#       lot of courses.
#
 

from Products.CMFCore.utils import getToolByName

def instname_to_inst(self):
    """ Copy the contents of the Instructor Name field to the new Institution Field. """

    portal_url = getToolByName(self, 'portal_url')
    portal = portal_url.getPortalObject()

    cbs = portal.portal_catalog(
        path={'query':'/'.join(portal.getPhysicalPath()) + '/'}, 
        portal_type='Course')

    for cb in cbs:
        course = cb.getObject()
        iname = course.getInstructorName()
        if iname:
            course.setInstitutionName(iname)
            course.setInstructorName('')
            course.reindexObject()

    return 'Instructor Name field successfully moved for all courses.\n'
