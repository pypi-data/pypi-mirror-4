from plone.app.testing import TEST_USER_NAME
from plone.app.testing import TEST_USER_PASSWORD
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import applyProfile
from plone.testing import z2

import unittest2 as unittest


class SlcShoppinglist(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        import slc.shoppinglist
        self.loadZCML('configure.zcml', package=slc.shoppinglist)

        z2.installProduct(app, 'slc.shoppinglist')

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'slc.shoppinglist:default')

    def tearDownZope(self, app):
        z2.uninstallProduct(app, 'slc.shoppinglist')


SLC_SHOPPINGLIST_FIXTURE = SlcShoppinglist()
INTEGRATION_TESTING = IntegrationTesting(
    bases=(SLC_SHOPPINGLIST_FIXTURE,),
    name="SlcShoppinglist:Integration")
FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(SLC_SHOPPINGLIST_FIXTURE,),
    name="SlcShoppinglist:Functional")


class FunctionalTestCase(unittest.TestCase):
    """Base class for functional tests."""

    layer = FUNCTIONAL_TESTING

    def getBrowser(self):
        """Create an instance of zope.testbrowser."""
        browser = z2.Browser(self.layer['app'])
        portal_url = self.layer['portal'].absolute_url()
        browser.open(portal_url + '/login_form')
        browser.getControl(name='__ac_name').value = SITE_OWNER_NAME
        browser.getControl(name='__ac_password').value = SITE_OWNER_PASSWORD
        browser.getControl(name='submit').click()
        self.assertIn('You are now logged in', browser.contents)
        browser.open(portal_url)
        return browser

    def viewError(browser):
        browser.getLink('see the full error message').click()
        file('/tmp/bla.html', 'w').write(browser.contents)
        import webbrowser
        import os
        if not os.fork():
            webbrowser.open('/tmp/bla.html')
            os._exit(0)
