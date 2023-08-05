from zope.publisher.browser import BrowserView


class ListingView(BrowserView):
    """ Base class for listing view """

    def _getListing(self, brains):
        if brains:
            numb = len(brains)
            num = numb/2
            if numb%2:
                num += 1
            return brains[:num], brains[num:]
        else:
            return [],[]


class SchoolListing(ListingView):
    """ List of Schools """

    def getSections(self):
        """ Get list of Schools """
        portal = self.context.portal_url.getPortalObject()
        brains = portal.portal_catalog.searchResults(
            path={'query':'/'.join(portal.getPhysicalPath())+'/',},
            Type='School',
            sort_on='sortable_title')
        return self._getListing(brains)


class DivisionListing(ListingView):
    """ List of divisions """

    def getSections(self):
        """ Get list of Divisions """
        brains = self.context.portal_catalog.searchResults(
            path={'query':'/'.join(self.context.getPhysicalPath())+'/',},
            Type='Division')
        return self._getListing(self, brains)
        
