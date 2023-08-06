import unittest2 as unittest
from mechanize import LinkNotFoundError
from zope.component import eventtesting

from plone.testing.z2 import Browser
from plone.app.testing import login
from plone.app.testing.interfaces import (
    SITE_OWNER_NAME,
    SITE_OWNER_PASSWORD,
    TEST_USER_ID,
    TEST_USER_NAME,
    TEST_USER_PASSWORD)

from ..testing import MY_PRODUCT_FUNCTIONAL_TESTING
from ..interfaces import IGroupRemoved


class CreateNewUserTests(unittest.TestCase):

    layer = MY_PRODUCT_FUNCTIONAL_TESTING

    def setUp(self):
        eventtesting.setUp()

    def tearDown(self):
        eventtesting.clearEvents()

    def _create_group(self, browser):
        portal = self.layer['portal']
        folder = portal['test-folder']
        browser.getLink(folder.Title()).click()
        browser.getLink('Sharing').click()
        browser.getLink('Add New Group').click()
        browser.getControl(name='addname').value = 'folder-members'
        browser.getControl(name='title:string').value = "Folder members"
        browser.getControl(name='localroles:list').value = ["Reader"]
        browser.getControl(name='form.button.Save').click()

    def _connect_as_manager(self):
        portal = self.layer['portal']
        app = self.layer['app']
        portalURL = portal.absolute_url()
        browser = Browser(app)
        browser.handleErrors = False
        browser.open(portalURL + '/login_form')
        browser.getControl(name='__ac_name').value = SITE_OWNER_NAME
        browser.getControl(name='__ac_password').value = SITE_OWNER_PASSWORD
        browser.getControl(name='submit').click()
        return browser

    def _connect_as_reviewer(self):
        portal = self.layer['portal']
        app = self.layer['app']
        portalURL = portal.absolute_url()
        browser = Browser(app)
        browser.handleErrors = False
        browser.open(portalURL + '/login_form')
        browser.getControl(name='__ac_name').value = TEST_USER_NAME
        browser.getControl(name='__ac_password').value = TEST_USER_PASSWORD
        browser.getControl(name='submit').click()
        return browser

    def test_create_new_group(self):
        self.browser = browser = self._connect_as_manager()
        self._create_group(browser)
#        open('/tmp/testbrowser.html', 'w').write(browser.contents)
        self.assertIn("remove-folder-members", browser.contents)

    def test_cant_create_new_group_as_reviewer(self):
        portal = self.layer['portal']
        folder = portal['test-folder']
        browser = self._connect_as_reviewer()
        browser.getLink(folder.Title()).click()
        browser.getLink('Sharing').click()
        with self.assertRaises(LinkNotFoundError):
            browser.getLink('Add New Group').click()

    def test_remove_group(self):
        browser = self._connect_as_manager()
        self._create_group(browser)
        browser.getControl(name="remove-folder-members").click()
        self.assertNotIn("remove-folder-members", browser.contents)
        self.assertIn("Folder members", browser.contents)
        events = eventtesting.getEvents(IGroupRemoved)
#        self.assertEqual(len(events), 1)
        self.assertTrue(len(events) > 1)

    def test_cant_remove_group_as_reviewer(self):
        browser = self._connect_as_manager()
        self._create_group(browser)
        browser = self._connect_as_reviewer()
        self.assertNotIn("remove-folder-members", browser.contents)
