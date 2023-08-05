# -*- coding: utf-8 -*-

from Products.Five import zcml
from Products.Five import fiveconfigure

from Testing import ZopeTestCase as ztc

from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import onsetup


@onsetup
def setup_product():
    """Set up additional products and ZCML required to test this product.

    The @onsetup decorator causes the execution of this body to be deferred
    until the setup of the Plone site testing layer.
    """

    fiveconfigure.debug_mode = True
    import collective.portlet.localcontents
    zcml.load_config('configure.zcml', collective.portlet.localcontents)
    fiveconfigure.debug_mode = False

    ztc.installPackage('collective.portlet.localcontents')

setup_product()
ptc.setupPloneSite(products=['collective.portlet.localcontents'])


class TestCase(ptc.PloneTestCase):
    """Base class used for test cases
    """


class FunctionalTestCase(ptc.FunctionalTestCase):
    """Test case class used for functional (doc-)tests
    """
