import plone.app.users.tests.base

from Testing import ZopeTestCase as ztc

from Zope2.App import zcml
from Products.Five import fiveconfigure
from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import onsetup, onteardown


@onsetup
def setup():
    import pmr2.captcha
    fiveconfigure.debug_mode = True
    zcml.load_config('configure.zcml', pmr2.captcha)
    zcml.load_config('test.zcml', pmr2.captcha.tests)
    fiveconfigure.debug_mode = False
    ztc.installPackage('pmr2.captcha')

@onteardown
def teardown():
    pass

setup()
teardown()
ptc.setupPloneSite(products=('pmr2.captcha',))


class TestCase(plone.app.users.tests.base.TestCase):
    """
    Extending the default test case to provide some marker helper.
    """
