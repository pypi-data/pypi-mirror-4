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

from Acquisition import aq_inner, aq_parent
from zope.component import getMultiAdapter
from Products.Five import BrowserView
from Products.statusmessages.interfaces import IStatusMessage
from enpraxis.educommons import eduCommonsMessageFactory as _
from Products.CMFCore.utils import getToolByName


class CreateTranslation(BrowserView):

    def _setCanonicalLanguage(self, obj):
        """Make sure an object has a language set (ie is not neutral).
        """
        lang=obj.Language()
        if not lang:
            portal_state=getMultiAdapter((self.context, self.request),
                                    name="plone_portal_state")
            lang=portal_state.language()
            obj.setLanguage(lang)



    def nextUrl(self, trans):
        """Figure out where users should go after creating the translation.
        """
        try:
            action=trans.getTypeInfo().getActionInfo("object/translate",
                    object=trans)
            return action["url"]
        except ValueError:
            pass

        try:
            action=trans.getTypeInfo().getActionInfo("object/edit",
                    object=trans)
            return action["url"]
        except ValueError:
            pass

        state=getMultiAdapter((trans, self.request), name="plone_context_state")
        return state.view_url()

    def __call__(self):
        status=IStatusMessage(self.request)
        self._setCanonicalLanguage(self.context)

        newlang=self.request["newlanguage"]

        if self.context.hasTranslation(newlang):
            state=getMultiAdapter((self.context, self.request),
                                    name="plone_context_state")
            status.addStatusMessage(_(u"Translation already exists"),
                                    type="error")
            return self.request.response.redirect(state.view_url())

        lt=getToolByName(self.context, "portal_languages")
        lt.setLanguageCookie(newlang)

        #Customization for eduCommons to ensure parent Division --> Course --> SubObject's parent folder translated first
        if self.context.aq_inner.aq_parent.Type() == 'Plone Site':
            self.context.addTranslation(newlang)
            trans=self.context.getTranslation(newlang)
            status.addStatusMessage(_(u"Translated created."),
                                    type="info")

            return self.request.response.redirect(self.nextUrl(trans))
        else:
            if self.context.aq_inner.aq_parent.aq_explicit.hasTranslation(newlang):
                self.context.addTranslation(newlang)
                trans=self.context.getTranslation(newlang)
                status.addStatusMessage(_(u"Translated created."),
                                        type="info")
                
                return self.request.response.redirect(self.nextUrl(trans))
            else:
                url = self.context.absolute_url()
                not_available = '%s/not_available_lang/view?set_language=%s&parentNotTranslated=True' % (url, newlang)
                return self.request.response.redirect(not_available)



