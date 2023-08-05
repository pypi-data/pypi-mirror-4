from Products.Five import zcml
from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import onsetup
from Testing import ZopeTestCase as ztc


@onsetup
def load_zcml():
    import collective.sharerizer
    zcml.load_config('configure.zcml', collective.sharerizer)
    ztc.installPackage('collective.sharerizer')

load_zcml()
ptc.setupPloneSite(products=['collective.sharerizer'])


class TestCase(ptc.PloneTestCase):
    """Test case class for doc tests"""


class FunctionalTestCase(ptc.FunctionalTestCase):
    """Test case class used for functional (doc-)tests
    """
