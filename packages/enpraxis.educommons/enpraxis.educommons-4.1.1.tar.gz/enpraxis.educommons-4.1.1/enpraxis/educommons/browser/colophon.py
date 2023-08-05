from plone.app.layout.viewlets import ViewletBase
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Acquisition import aq_inner
from zope.component import getMultiAdapter
from AccessControl import getSecurityManager
from zope.component import getMultiAdapter
from Products.CMFCore.utils import getToolByName


class eduCommonsColophonViewlet(ViewletBase):
    """ Viewlet for eduCommons """

    index = ViewPageTemplateFile('colophon.pt')

    def update(self):
        cs = getMultiAdapter((self.context, self.request),
                             name=u'plone_context_state')
        self.colophon_actions = cs.actions('eccolophon_actions')
        self.portal_state = getMultiAdapter((self.context, self.request),
                                            name=u'plone_portal_state')
        qi = getToolByName(self.context, 'portal_quickinstaller')
        self.version = qi.getProductVersion('enpraxis.educommons')
        self.anonymous = self.portal_state.anonymous()
        if self.anonymous:
            self.username = None
        else:
            member = self.portal_state.member()
            uname = self.getUserName(member)
            roles = self.getRoles(member)
            if roles:
                self.username = '%s (%s)' %(uname, roles)
            else:
                self.username = uname
            self.homelink = "%s/personalize_form" % (
                self.portal_state.navigation_root_url())

            
    def getUserName(self, member):
        """ Get fullname of user or id """
        userid = member.getId()
        ms = getToolByName(self.context, 'portal_membership')
        minfo = ms.getMemberInfo(userid)
        if minfo['fullname']:
            username = minfo.get('fullname')
        else:
            username = userid
        return username
        
    def getRoles(self, member):
        """ Get user roles """
        roles = ''
        for x in member.getRoles():
            if x not in ['Authenticated', 'Member']:
                if roles:
                    roles += ', '
                roles += x
        return roles

    def getVersion(self):
        """ Get the current version of eduCommons """
        import pdb; pdb.set_trace()
        qi = getToolByName(self.context, 'portal_quickinstaller')
        return qi.getProductVersion('enpraxis.educommons')
