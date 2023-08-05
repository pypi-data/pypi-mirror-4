from Testing import ZopeTestCase as ztc
from Products.Five import zcml
from Products.Five import fiveconfigure
from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import onsetup

@onsetup
def setup_package():
    fiveconfigure.debug_mode = True
    import fourdigits.portlet.twitter
    zcml.load_config('configure.zcml', fourdigits.portlet.twitter)
    fiveconfigure.debug_mode = False
    ztc.installPackage('fourdigits.portlet.twitter')

setup_package()
ptc.setupPloneSite(extension_profiles=(
    'fourdigits.portlet.twitter:default',
))

class TestCase(ptc.PloneTestCase):
    """Base class used for test cases
    """

class FunctionalTestCase(ptc.FunctionalTestCase):
    """Test case class used for functional (doc-)tests
    """
