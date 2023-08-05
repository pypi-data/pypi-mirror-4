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

from Products.CMFPlone.utils import _createObjectByType
from Products.CMFCore.utils import getToolByName
from zope.component import getUtility, getMultiAdapter
from plone.portlets.interfaces import IPortletManager, IPortletAssignmentMapping
from enpraxis.educommons import portlet
from utilities.interfaces import IECUtility
from utilities.utils import eduCommonsUtility
from zope.app.component.interfaces import ISite
from zope.app.component.hooks import setSite
from zope.component import getSiteManager
from eventHandlers import syndicateFolderishObject
from zope.component.interfaces import ComponentLookupError
from zope.annotation.interfaces import IAnnotations
from enpraxis.educommons import eduCommonsMessageFactory as _


# setup handlers for eduCommons

def importFinalSteps(context):
    site = context.getSite()
    # Do not run if already loaded
    if context.readDataFile('enpraxis_educommons_setup.txt') is None:
        return
    setupDefaultPortlets(site)
    defaultSettings(site)
    setupUtilities(site)
    setupControlPanel(site)
    setupTransforms(site)
    customizeAddOnProducts(site)

def importContent(context):
    site = context.getSite()
    # Do not run if already loaded
    if context.readDataFile('enpraxis_educommons_setup.txt') is None:
        return
    if getattr(site, 'REQUEST', None):
        if site.REQUEST.has_key('title'):
            site.setTitle(site.REQUEST['title'])
    setupPortalContent(site)

def setupUtilities(site):
    """ Register a local utility """

    sm = getSiteManager()
    if not sm.queryUtility(IECUtility):
        sm.registerUtility(eduCommonsUtility('educommonsutility'),
                        IECUtility)

def setupControlPanel(site):
    """ Tweak Control Panel conditions  """
    from Products.CMFCore.Expression import Expression
    control_panel = site.portal_controlpanel

    panels = ['ZMI', 'NavigationSettings', 'QuickInstaller', 'TypesSettings', 'portal_atct', 'errorLog']
    actions = control_panel.listActions()

    for panel in panels:
        for action in actions:
            if panel == action.id:
                action.condition = Expression('python:"Manager" in here.portal_membership.getAuthenticatedMember().getRoles()')

def setupTransforms(portal):
    from Products.CMFDefault.utils import VALID_TAGS
    from Products.CMFDefault.utils import NASTY_TAGS

    valid_tags = VALID_TAGS.copy()
    nasty_tags = NASTY_TAGS.copy()

    nasty_tags.pop('applet')
    nasty_tags.pop('embed')
    nasty_tags.pop('object')
    nasty_tags.pop('script')

    valid_tags['applet'] = 1
    valid_tags['embed'] = 1
    valid_tags['object'] = 1
    valid_tags['thead'] = 1
    valid_tags['tfoot'] = 1
    valid_tags['param'] = 1

    kwargs = {'nasty_tags': nasty_tags,
              'valid_tags': valid_tags,
              'remove_javascript': 0}

    transform = getattr(getToolByName(portal, 'portal_transforms'), 'safe_html')

    for k in list(kwargs):
        if isinstance(kwargs[k], dict):
            v = kwargs[k]
            kwargs[k+'_key'] = v.keys()
            kwargs[k+'_value'] = [str(s) for s in v.values()]
            del kwargs[k]

    transform.set_parameters(**kwargs)
    transform._p_changed = True
    transform.reload()


def setupPortalContent(portal):
    """ Setup default eduCommons content """

    existing = portal.objectIds()
    wftool = getToolByName(portal, 'portal_workflow')

    syndicateFolderishObject(portal, event=None)

    # If Members, news, and/or event objects exist, remove them
    delobjs = []
    if 'Members' in existing:
        delobjs.append('Members')
    if 'news' in existing:
        delobjs.append('news')
    if 'events' in existing:
        delobjs.append('events')
    if delobjs:
        portal.manage_delObjects(delobjs)

    # Add the Course List
    cid = 'courselist'
    if cid not in existing:
        # Create a new course list
        title = _(u'course_list_title', default=u'Courses')
        ttitle = portal.translate(title)
	descr = _(u'course_list_description', default=u'A list of courses on this site.')
        tdescr = portal.translate(descr) 
        _createObjectByType('CoursesTopic', portal, id=cid, title=ttitle,
                            description=tdescr)
        courselist = getattr(portal, cid)
        # Set the criterion for the course list smart folder
        crit = courselist.addCriterion('Type', 'ATPortalTypeCriterion')
        crit.setValue('Division')
        courselist.setSortCriterion('sortable_title', reversed=False)
        courselist.setLayout('courses_listing')
        # publish it
        if wftool.getInfoFor(courselist, 'review_state') != 'published':
            wftool.doActionFor(courselist, 'publish')


    fptitle = _(u'frontpage_educommons_welcome', 
                default=u'Welcome to eduCommons')
    tfptitle = portal.translate(fptitle)
    fpdescr = _(u'frontpage_educommons_description', 
                default=u'eduCommons provides access to educational materials more commonly known as OpenCourseWare.')
    tfpdescr = portal.translate(fpdescr)
    if 'front-page' not in existing:
        _createObjectByType('Document', portal, id='front-page', title=tfptitle,
                            description=tfpdescr)
    fpage = getattr(portal, 'front-page')
    if 'Plone' in fpage.title:
        fpage.setTitle(tfptitle)
        fpage.setDescription(tfpdescr)
        template = '@@frontpage_view'
        # Need try/except for QuickInstaller installations of 3rd party products
        try:
            template = fpage.restrictedTraverse(str(template))       
            text = template(fpage)
            fpage.setText(text)
            publishObject(fpage)
        except AttributeError:
            pass

    # Add About
    aid = 'about'
    if aid not in existing:
        atitle = _(u'about_ocw_title', default=u'About OCW')
        tatitle = portal.translate(atitle)
        adescr = _(u'about_ocw_descr', default=u'Current information about this OpenCourseWare site.')
        tadescr = portal.translate(adescr)
        _createObjectByType('Folder', 
                            portal, 
                            id=aid, 
                            title=tatitle,
                            description=tadescr)
        about = getattr(portal, aid)
        publishObject(about)
        _createObjectByType('Document', 
                            about, 
                            id='abouttext_text',
                            title=tatitle, 
                            description=tadescr)
        context = about.abouttext_text
        
        publishObject(about.abouttext_text)
        template = '@@abouttext_view'
        template = context.restrictedTraverse(str(template))
        text = template(context)
        context.setText(text)
        context.setPresentation(True)

        about.setDefaultPage('abouttext_text')

        #Terms of Use
        _createObjectByType('Document', about, id="terms-of-use", title="Terms of Use", 
                            description='Terms of use for this web site.')
        context = getattr(about, 'terms-of-use')
        publishObject(context)
        template = '@@tou_view'
        template = context.restrictedTraverse(str(template))
        text = template(context)
        context.setText(text)

        #Privacy Policy
        _createObjectByType('Document', about, id="privacy-policy", title="Privacy Policy", 
                            description='The privacy policy for this web site.')
        context = getattr(about, 'privacy-policy')
        publishObject(context)
        template = '@@privacypolicy_view'
        template = context.restrictedTraverse(str(template))
        text = template(context)
        context.setText(text)

    # Add top level Help folder
    hid = 'help'
    if hid not in existing:
        htitle = _(u'help_folder_title', default=u'Help')
        thtitle = portal.translate(htitle)
        hdescr = _(u'help_folder_descr', default=u'Get help and further information.')
        thdescr = portal.translate(hdescr)
        _createObjectByType('Folder', 
                            portal, 
                            id=hid, 
                            title=thtitle,
                            description=thdescr)
        help = getattr(portal, hid)
        publishObject(help)

        # Add default help document
        _createObjectByType('Document',
                            help,
                            id='help_text',
                            title=thtitle,
                            description=thdescr)
        context = help.help_text
        publishObject(context)
        template = '@@faq_view'
        template = context.restrictedTraverse(str(template))
        text = template(context)
        context.setText(text)
        context.setTableContents(True)
        help.setDefaultPage('help_text')

        # Add accessibility guidelines
        _createObjectByType('Document', 
                            help, 
                            id="accessibility-guidelines", 
                            title="Accessibility Guidelines",
                            description='Guidelines to help determine if content meets accessibility standards.')
        context = getattr(help, 'accessibility-guidelines')
        publishObject(context)
        template = '@@accessibilityguidelines_view'
        template = context.restrictedTraverse(str(template))
        text = template(context)
        context.setText(text)

    # Add Feedback folder
    fid = 'feedback'
    if fid not in existing:
        ftitle = _(u'feedback_folder_title', default=u'Feedback')
        tftitle = portal.translate(ftitle)
        fdescr = _(u'feedback_folder_descr', default=u'Please send us your feedback.')
        tfdescr = portal.translate(fdescr)
        _createObjectByType('Feedback', 
                            portal, 
                            id=fid, 
                            title=tftitle,
                            description=tfdescr)
        feedback = getattr(portal, fid)
        publishObject(feedback)
        feedback.setLayout('feedback_view')

        _createObjectByType('Document', feedback, id='thanks', title='Thank You',
                            description='')
        feedback.thanks.setText('Thank you for your feedback.')
        feedback.thanks.setExcludeFromNav(True)
        publishObject(feedback.thanks)
        feedback.thanks.reindexObject()
 
def publishObject(context):
    """ Move an object into the published state """
    wftool =  getToolByName(context, 'portal_workflow')


    if wftool.getInfoFor(context, 'review_state') != 'Published':
        wftool.doActionFor(context, 'submit')
        wftool.doActionFor(context, 'release')
        wftool.doActionFor(context, 'publish')        

           
        
def setupDefaultPortlets(portal):
    """ Setup default portlets for eduCommons """

    leftColumn = getUtility(IPortletManager, name=u'plone.leftcolumn', context=portal)
    left = getMultiAdapter((portal, leftColumn), IPortletAssignmentMapping, context=portal)

    # Add the eduCommons custom simple navigation portlet
    if u'Simple Nav Portlet' not in left:
        left[u'Simple Nav Portlet'] = portlet.simplenavportlet.Assignment()

    # Turn off other left hand portlets
    if u'navigation' in left:
        del left[u'navigation']
    if u'login' in left:
        del left[u'login']
    if u'recent' in left:
        del left[u'recent']

    rightColumn = getUtility(IPortletManager, name=u'plone.rightcolumn', context=portal)
    right = getMultiAdapter((portal, rightColumn), IPortletAssignmentMapping, context=portal)

    if u'Course Builder Portlet' not in right:
        right[u'Course Builder Portlet'] = portlet.coursebuilder.Assignment()

    # Turn off right hand portlets
    if u'review' in right:
        del right[u'review']

    if u'news' in right:
        del right[u'news']

    if u'events' in right:
        del right[u'events']

    if u'calendar' in right:
        del right[u'calendar']

def defaultSettings(portal):
    """ Miscellaneous settings  """

    # Change allow_content_types for Site
    pt = portal.portal_types
    site = getattr(pt, 'Plone Site')
    site.filter_content_types = 1
    site.allowed_content_types = ('Topic', 'Division', 'Folder', 'Document', 'Link', 'File', 'Image', 'CoursesTopic', 'Feedback')


    # Give the MailHost a Title
    #mailhost = getattr(site, 'MailHost')
    #mailhost.title = 'Plone Mail Host'
    
    # Change allow_content_types for Folder
    # Modifying it in setuphandlers allows us to maintain one less content type
    folder = getattr(pt, 'Folder')
    folder.filter_content_types = 1
    folder.allowed_content_types = ('FSSFile','Folder', 'Document', 'Link', 'File', 'Image')

    # Update default types for Wiki Behaviour
    import plone
    wicked_type_regs = {'Page': plone.app.controlpanel.markup.wicked_type_regs['Page']}
    plone.app.controlpanel.markup.wicked_type_regs = wicked_type_regs

    portal.portal_properties.educommons_properties.division_descriptor = _(u'Departments')

    #Update Sitewide Default Syndication Properties
    portal.portal_syndication.max_items = 999

def customizeAddOnProducts(portal):
    """ Customizations to dependent products  """

    #Move PloneBookmarklets document actions to bottom of the list
    dactions = portal.portal_actions.document_actions
    if 'bookmarklets' in dactions:
        dactions.moveObjectsToBottom(('bookmarklets',))

def getTranslatedObjInfo(context, msgid, default):
    """ Get a translated version of the object's information (id, title, desc) """
    objstr = _(msgid, default=default)
    return context.translate(objstr)
