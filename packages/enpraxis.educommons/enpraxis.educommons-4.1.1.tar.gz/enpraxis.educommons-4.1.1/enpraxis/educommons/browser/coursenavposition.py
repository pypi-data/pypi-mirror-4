from zope.publisher.browser import BrowserView
from enpraxis.educommons.annotations.interfaces import ICourseOrderable, ICourseOrder


class CourseNavPosition(BrowserView):
    """ Adjust course navigation position for objects in a course """

    def __call__(self):
        position = self.request['position']
        url = self.request['url']
        objs = self.getNavObjects()

        # Check if course is first, if not fix it
        if objs:
            if objs[0].Type != 'Course':
                for x in range(len(objs)):
                    if x != 0:
                        if objs[x].Type == 'Course':
                            objs[0], objs[x] = objs[x], objs[0]
                            self.resetOrder(objs)
                            break

        # find object in list
        for x in range(len(objs)):
            if url == objs[x].getPath():
                if 'up' == position:
                    if x > 1:
                        objs[x-1], objs[x] = objs[x], objs[x-1]
                        self.resetOrder(objs)
                elif 'down' == position:
                    if x != 0 and len(objs) > 2 and x < len(objs) - 1:
                        objs[x], objs[x+1] = objs[x+1], objs[x]
                        self.resetOrder(objs)
                break

        self.request.response.redirect('order_courseobjs')

    def getNavObjects(self):
        """ Get navigation objects for reordering """
        qpath = '/'.join(self.context.getPhysicalPath())+'/'
        contentFilter={'path':{'query':qpath},
                       'sort_on':'getObjPositionInCourse'}
        brains = self.context.portal_catalog.searchResults(contentFilter)
        return [brain for brain in brains if not getattr(brain.aq_explicit, 'exclude_from_nav', True)]

    def resetOrder(self, objs):
        """ Reorder objects in course """
        index = 0
        for obj in objs:
            ob = obj.getObject()
            if ICourseOrderable.providedBy(ob):
                co = ICourseOrder(ob)
                co.position = index
                ob.reindexObject()
                index += 1


        
