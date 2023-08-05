from plone.app.layout.viewlets import ViewletBase
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Acquisition import aq_inner
from zope.component import getMultiAdapter
from AccessControl import getSecurityManager


class eduCommonsFooterViewlet(ViewletBase):
    """ Viewlet for eduCommons footer information """

    index = ViewPageTemplateFile('footer.pt')

    def update(self):
        context_state = getMultiAdapter((self.context, self.request),
                                        name=u'plone_context_state')

        self.footer_actions = context_state.actions('ecfooter_actions')


        
