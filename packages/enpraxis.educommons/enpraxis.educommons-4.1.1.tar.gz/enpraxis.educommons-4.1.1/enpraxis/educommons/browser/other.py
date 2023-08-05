from zope.publisher.browser import BrowserView
from zope.component import getMultiAdapter
from Acquisition import aq_inner

class OtherView(BrowserView):
    """ Other view """

    def getActionItems(self):
        """ get Additional Action items """
        context = aq_inner(self.context)
        context_state = getMultiAdapter((context, self.request),
                                        name=u'plone_context_state')
        return context_state.actions(category='other_options')

