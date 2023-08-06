# integration and functional tests
# see http://plone.org/documentation/tutorial/testing/writing-a-plonetestcase-unit-integration-test
# for more information about the following setup

from Products.Five import zcml
from Products.Five import fiveconfigure
from Products.Five.testbrowser import Browser
from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import onsetup


@onsetup
def setup_product():
    fiveconfigure.debug_mode = True
    import collective.gsa
    zcml.load_config('configure.zcml', collective.gsa)
    fiveconfigure.debug_mode = False

setup_product()
ptc.setupPloneSite(extension_profiles=(
    'collective.gsa:default',
))


class GSATestCase(ptc.PloneTestCase):
    """ base class for integration tests """


class GSAFunctionalTestCase(ptc.FunctionalTestCase):
    """ base class for functional tests """

    def getBrowser(self, loggedIn=True):
        """ instantiate and return a testbrowser for convenience """
        browser = Browser()
        if loggedIn:
            user = ptc.default_user
            pwd = ptc.default_password
            browser.addHeader('Authorization', 'Basic %s:%s' % (user, pwd))
        return browser

    def setStatusCode(self, key, value):
        from ZPublisher import HTTPResponse
        HTTPResponse.status_codes[key.lower()] = value

