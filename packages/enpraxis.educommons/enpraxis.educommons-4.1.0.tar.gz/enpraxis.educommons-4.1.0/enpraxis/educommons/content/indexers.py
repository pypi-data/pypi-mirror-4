from plone.indexer import indexer
from Products.ATContentTypes.interface import IATDocument
from enpraxis.educommons.interfaces import ICourse


@indexer(IATDocument)
def getOerType(object):
    # Check to see if Document has been extended yet
    if object.Schema().has_key('oerType'):
        return object.Schema()['oerType'].get(object)
    else:
        return None

@indexer(ICourse)
def getFullCourseName(object):
    ftitle = ''
    id = object.getCourseId()
    title = object.Title()
    term = object.getTerm()
    if id:
        ftitle = '%s - ' %id
    ftitle += title
    if term:
        ftitle += ', %s' %term
    return ftitle

    
