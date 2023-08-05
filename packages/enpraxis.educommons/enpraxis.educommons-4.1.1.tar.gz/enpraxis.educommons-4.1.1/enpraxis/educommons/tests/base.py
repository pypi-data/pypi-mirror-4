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

from zope.testing import doctest
from zope.testing.doctestunit import DocFileSuite
from Testing import ZopeTestCase
from Testing.ZopeTestCase import FunctionalDocFileSuite, ZopeDocFileSuite, Functional
from Testing.ZopeTestCase import ZopeDocFileSuite
from Products.PloneTestCase.PloneTestCase import PloneTestCase
from Products.PloneTestCase.PloneTestCase import FunctionalTestCase, setupPloneSite, installProduct, installPackage
from setuptools import find_packages

from Products.Five import zcml
from Products.Five import fiveconfigure
from Products.PloneTestCase.layer import onsetup
from Testing import ZopeTestCase as ztc
from Products.CMFPlone.tests import dummy

@onsetup
def setup_educommons_project():
    """Set up the additional products required for the borg.project tests.
    
    The @onsetup decorator causes the execution of this body to be deferred
    until the setup of the Plone site testing layer.
    """
    
    # Load the ZCML configuration for the enpraxis.educommons package.
    # This includes the other products below as well.
    
    fiveconfigure.debug_mode = True

    import enpraxis.educommons
    import collective.contentlicensing
    import collective.zipfiletransport
    import collective.imstransport
    import collective.plonebookmarklets
    import enpraxis.leftskin
    zcml.load_config('configure.zcml', enpraxis.educommons)
    zcml.load_config('configure.zcml', collective.contentlicensing)
    zcml.load_config('configure.zcml', collective.zipfiletransport)
    zcml.load_config('configure.zcml', collective.imstransport)
    zcml.load_config('configure.zcml', collective.plonebookmarklets)
    zcml.load_config('configure.zcml', enpraxis.leftskin)
    fiveconfigure.debug_mode = False
    
    # We need to tell the testing framework that these products
    # should be available. This can't happen until after we have loaded
    # the ZCML. Notice the extra package=True argument passed to 
    # installProduct() - this tells it that these packages are *not* in the
    # Products namespace.
    
    ztc.installPackage('collective.contentlicensing')
    ztc.installPackage('collective.zipfiletransport')
    ztc.installPackage('collective.imstransport')
    ztc.installPackage('collective.plonebookmarklets')
    ztc.installPackage('enpraxis.leftskin')
    ztc.installPackage('enpraxis.educommons')
    ztc.installProduct('ProxyIndex')
    
# The order here is important: We first call the (deferred) function which
# installs the products we need for the package. Then, we let 
# PloneTestCase set up on installation.

setup_educommons_project()
setupPloneSite(with_default_memberarea=0, extension_profiles=['collective.contentlicensing:default','collective.zipfiletransport:default','collective.imstransport:default','collective.plonebookmarklets:default','enpraxis.leftskin:default','enpraxis.educommons:default'])           


oflags = (doctest.ELLIPSIS |
          doctest.NORMALIZE_WHITESPACE)
prod = 'enpraxis.educommons'

class eduCommonsTestCase(PloneTestCase):
    """ 
    Unit test package for eduCommonsTestCase
    """
    def _setupHomeFolder(self):
        """ Ugly hack to keep the underlying testing framework from trying to create
            a user folder. """
        pass

    def addTestDocument(self,id='test-document',context=None):
        context.invokeFactory('Document', id)
        context.portal_factory.doCreate(context,id)
        return getattr(context, id)

    def addTestImage(self, id='test-image',context=None):
        context.invokeFactory('Image', id, file=dummy.Image() )
        return getattr(context, id)

    def addTestFile(self,id='test-file',context=None):
        context.invokeFactory('File', id, file=dummy.File() )
        return getattr(context, id)

    def addTestDepartment(self,id='test-dept'):
        context = self.portal
        context.invokeFactory('Division', id)
        return getattr(context, id)

    def addTestCourse(self,id='test-course', context=None):
        context.invokeFactory('Course', id)
        return getattr(context,id)

class eduCommonsFunctionalTestCase(Functional, eduCommonsTestCase):
    """ Base class for functional integration tests. """


