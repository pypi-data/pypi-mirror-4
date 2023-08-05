from OFS.Application import install_package
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
    import Products.BlingPortlet
    zcml.load_config('configure.zcml', Products.BlingPortlet)
    ztc.installProduct('BlingPortlet')
    fiveconfigure.debug_mode = False
    
setup_product()
ptc.setupPloneSite(products=['BlingPortlet'])

class TestCase(ptc.PloneTestCase):
    """Base class used for test cases
    """
        
class FunctionalTestCase(ptc.FunctionalTestCase):
    """Test case class used for functional (doc-)tests
    """