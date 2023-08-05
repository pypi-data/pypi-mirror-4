##################################################################################
#    Copyright (c) 2009 Massachusetts Institute of Technology, All rights reserved.
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
##################################################################################

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
def setup_oaiintercom_project():
    """
    The @onsetup decorator causes the execution of this body to be deferred
    until the setup of the Plone site testing layer.
    """
    
    # Load the ZCML configuration for the collective.oaiintercom package

    fiveconfigure.debug_mode = True

    import collective.oaiintercom
    zcml.load_config('configure.zcml', collective.oaiintercom)
    fiveconfigure.debug_mode = False
    
    # We need to tell the testing framework that these products
    # should be available. This can't happen until after we have loaded
    # the ZCML. Notice the extra package=True argument passed to 
    # installProduct() - this tells it that these packages are *not* in the
    # Products namespace.
    
    ztc.installPackage('collective.oaiintercom')

    
# The order here is important: We first call the (deferred) function which
# installs the products we need for the package. Then, we let 
# PloneTestCase set up on installation.

setup_oaiintercom_project()
setupPloneSite(with_default_memberarea=0, extension_profiles=['collective.oaiintercom:default',])           


oflags = (doctest.ELLIPSIS |
          doctest.NORMALIZE_WHITESPACE)
prod = 'collective.oaiintercom'

class oaiintercomTestCase(PloneTestCase):
    """ Base Test Case"""

class oaiintercomFunctionalTestCase(Functional, oaiintercomTestCase):
    """ Base class for functional integration tests. """


