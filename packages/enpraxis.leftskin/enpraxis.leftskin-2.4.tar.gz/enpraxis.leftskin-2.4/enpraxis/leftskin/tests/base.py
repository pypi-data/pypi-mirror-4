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


packages=find_packages('src'),
package_dir = {'': 'src'},

@onsetup
def setup_leftskin_project():
    """Set up the additional products required for the borg.project tests.
    
    The @onsetup decorator causes the execution of this body to be deferred
    until the setup of the Plone site testing layer.
    """
    
    # Load the ZCML configuration for the enpraxis.leftskin package

    fiveconfigure.debug_mode = True

    import enpraxis.leftskin
    zcml.load_config('configure.zcml', enpraxis.leftskin)
    fiveconfigure.debug_mode = False
    
    # We need to tell the testing framework that these products
    # should be available. This can't happen until after we have loaded
    # the ZCML. Notice the extra package=True argument passed to 
    # installProduct() - this tells it that these packages are *not* in the
    # Products namespace.
    
    ztc.installPackage('enpraxis.leftskin')

    
# The order here is important: We first call the (deferred) function which
# installs the products we need for the package. Then, we let 
# PloneTestCase set up on installation.

setup_leftskin_project()
setupPloneSite(with_default_memberarea=0, extension_profiles=['enpraxis.leftskin:default',])           


oflags = (doctest.ELLIPSIS |
          doctest.NORMALIZE_WHITESPACE)
prod = 'enpraxis.leftskin'

class leftskinTestCase(PloneTestCase):
    """ 
    Unit test package for lefstkinTestCase
    """
    def _setupHomeFolder(self):
        """ Ugly hack to keep the underlying testing framework from trying to create
            a user folder. """
        pass

class leftskinFunctionalTestCase(Functional, leftskinTestCase):
    """ Base class for functional integration tests. """


