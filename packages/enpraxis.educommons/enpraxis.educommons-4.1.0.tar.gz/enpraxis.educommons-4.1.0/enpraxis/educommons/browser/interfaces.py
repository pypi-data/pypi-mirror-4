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


from zope.publisher.interfaces.browser import IBrowserView
from zope.viewlet.interfaces import IViewletManager
from zope.interface import Interface
from zope import schema
from zope.schema import Iterable
from enpraxis.educommons import eduCommonsMessageFactory as _


class ITemplateForm(Interface):
    """ Template form. """

    template = schema.Choice(title=_(u'Template Selector'),
                           description=_(u'Choose a template to apply to your object.'),
                           required=True,
                           vocabulary="Template Choices")

class IFeedbackForm(Interface):
    """ Feedback form for end users. """

    name = schema.TextLine(title=_(u'Name'),
                           description=_(u'Please Provide us with your name so we know who you are.'),
                           required=False)

    email = schema.TextLine(title=_(u'Email'),
                            description=_(u'Please provide us with your email so that we can contact you if necessary.'),
                            required=False)

    subject = schema.TextLine(title=_(u'Subject'),
                              description=_(u'A simple statement indicating the nature of your feedback.'),
                              required=False)

    body = schema.Text(title=_(u'Comments'),
                       description=_(u'Please include any comments you would like us to hear.'),
                       required=True)

class IReportContentForm(Interface):
    """ Report Content form for end users. """

    name = schema.TextLine(title=_(u'Name'),
                           description=_(u'Please provide us with your name so we know who you are.'),
                           required=False)

    email = schema.TextLine(title=_(u'Email'),
                            description=_(u'Please provide us with your email so that we can contact you if necessary.'),
                            required=False)

    body = schema.Text(title=_(u'Comments'),
                       description=_(u'Please provide comments regarding the nature of the inappropriate content.'),
                       required=True)



class IAfterTitle(IViewletManager):
    """ Marker interface for after title viewlet manager. """


class IeduCommonsSharingPageRole(Interface):
    """A named utility providing information about roles that are managed
    by the sharing page.
    
    Utility names should correspond to the role name.
    """
    
    title = schema.TextLine(title=_(u"A friendly name for the role"))
    
    required_permission = schema.TextLine(title=_(u"Permission required to manage this local role"),
                                          required=False)
