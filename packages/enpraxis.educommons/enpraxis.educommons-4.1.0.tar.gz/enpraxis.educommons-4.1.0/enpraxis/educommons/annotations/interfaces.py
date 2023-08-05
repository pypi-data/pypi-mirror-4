from zope.interface import Interface
from zope.annotation.interfaces import IAnnotatable


class IClearCopyrightable(IAnnotatable):
    """ Marker interface for clear copyright flag """

class IClearCopyright(Interface):
    """ Clear copyright interface """

class IAccessibilityCompliantable(IAnnotatable):
    """ Marker interface for accessibility compliance flag """

class IAccessibilityCompliant(Interface):
    """ Accessibility compliance interface """

class ICourseOrderable(IAnnotatable):
    """ Marker interface for object position in course """

class ICourseOrder(Interface):
    """ Object position in course interface """
