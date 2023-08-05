from slc.shoppinglist.tests.base import FunctionalTestCase

import unittest2 as unittest


class Stories(FunctionalTestCase):

    def setUp(self):
        self.portal = self.layer['portal']
        self.portal.error_log._ignored_exceptions = ()
        self.portal_url = self.portal.absolute_url()

    def testAddContentToShoppinglist(self):
        """
        We create a content item and add it to the shoppinglist
        """
        browser = self.getBrowser()
        browser.getLink('Link').click()
        browser.getControl('Title').value  = 'My Item'
        browser.getControl('URL').value = "http://nohost.com"
        browser.getControl('Save').click()
        self.assertTrue('Changes saved' in browser.contents)
        browser.open('/'.join(browser.url.split('/')[:-1] +
                              ['my-item', 'add_to_shoppinglist']))
        self.assertTrue('"My Item" added to shoppinglist' in browser.contents)

    def testRemoveItemFromShoppinglist(self):
        """
        We add an item to the shoppinglist, which we remove afterwards
        """
        browser = self.getBrowser()
        browser.getLink('Link').click()
        browser.getControl('Title').value  = 'My Item'
        browser.getControl('URL').value = "http://nohost.com"
        browser.getControl('Save').click()
        browser.open('/'.join(browser.url.split('/')[:-1] +
                              ['my-item', 'add_to_shoppinglist']))
        browser.open('/'.join(browser.url.split('/')[:-1] +
                              ['shoppinglistedit']))
        self.assertTrue("My Item</a> (http://nohost/plone/my-item)"
                        in browser.contents)
        browser.getControl(name='form.uids.0').value = "selected"
        browser.getControl('Remove').click()
        self.assertTrue("My Item</a> (http://nohost/plone/my-item)"
                        not in browser.contents)

    def testClearEntireList(self):
        """
        We add 2 items to the shoppinglist, and then clear it again
        """
        browser = self.getBrowser()
        browser.getLink('Link').click()
        browser.getControl('Title').value  = 'My Item'
        browser.getControl('URL').value = "http://nohost.com"
        browser.getControl('Save').click()
        browser.open('/'.join(browser.url.split('/')[:-1] +
                              ['my-item', 'add_to_shoppinglist']))
        browser.getLink('Home').click()
        browser.getLink('Link').click()
        browser.getControl('Title').value  = 'My other Item'
        browser.getControl('URL').value = "http://nohost.com"
        browser.getControl('Save').click()
        browser.open('/'.join(browser.url.split('/')[:-1] +
                              ['my-other-item', 'add_to_shoppinglist']))
        browser.open('/'.join(browser.url.split('/')[:-1] +
                              ['shoppinglistedit']))
        browser.getControl(name='form.actions.clear').click()
        # Since we didn't tick the "Clear entire shoppinglist" checkbox, both
        # items should still be there
        self.assertTrue("My Item</a> (http://nohost/plone/my-item)"
                        in browser.contents)
        self.assertTrue("My other Item</a> (http://nohost/plone/my-other-item)"
                        in browser.contents)
        browser.getControl(name='form.clearList').value = 'selected'
        browser.getControl(name='form.actions.clear').click()
        self.assertTrue("My Item</a> (http://nohost/plone/my-item)"
                        not in browser.contents)
        self.assertTrue("My other Item</a> (http://nohost/plone/my-other-item)"
                        not in browser.contents)


def test_suite():
    """This sets up a test suite that actually runs the tests in the class(es)
    above.
    """
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
