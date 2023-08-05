from plone.indexer import indexer
from interfaces import IClearCopyrightable, IClearCopyright
from interfaces import IAccessibilityCompliantable, IAccessibilityCompliant
from interfaces import ICourseOrderable, ICourseOrder


@indexer(IClearCopyrightable)
def getCopyrightCleared(object):
    clear = IClearCopyright(object)
    return clear.clearedcopyright


@indexer(IAccessibilityCompliantable)
def getAccessibilityCompliant(object):
    access = IAccessibilityCompliant(object)
    return access.accessible


@indexer(ICourseOrderable)
def getPositionInCourse(object):
    pos = ICourseOrder(object)
    return pos.position
   
