import unittest2 as unittest
from plone.app.testing import logout
from rt.atmigrator.testing import ATMIGRATOR_INTEGRATION_TESTING
from zope.component import getMultiAdapter
from plone.testing.z2 import Browser
from plone.app.testing import TEST_USER_NAME, TEST_USER_PASSWORD, SITE_OWNER_NAME, SITE_OWNER_PASSWORD


class TestATMigratorView(unittest.TestCase):

    layer = ATMIGRATOR_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']

    def test_migrate_view_access(self):
        """
        test if there is migrate view
        """
        view = getMultiAdapter((self.portal, self.request), name="migrate-types")
        view = view.__of__(self.portal)
        self.failUnless(view())

    def test_migrate_view_protected(self):
        """
        test if the view is protected
        """
        from AccessControl import Unauthorized
        logout()
        self.assertRaises(Unauthorized, self.portal.restrictedTraverse, '@@migrate-types')


class TestATMigratorFunctional(unittest.TestCase):

    layer = ATMIGRATOR_INTEGRATION_TESTING

    def setUp(self):
        app = self.layer['app']
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        self.portal_url = self.portal.absolute_url()
        self.browser = Browser(app)
        self.browser.addHeader('Authorization', 'Basic %s:%s' % (SITE_OWNER_NAME, SITE_OWNER_PASSWORD,))

    def test_migrate_cancel_view(self):
        """
        """
        self.browser.open("%s/@@migrate-types" % self.portal_url)
        self.assertTrue(u"Migrate content-types" in self.browser.contents)
        self.browser.getControl(name='form.button.Cancel').click()
        self.assertTrue("Migration canceled." in self.browser.contents)

    def test_migrate_submit_view(self):
        """
        """
        self.browser.open("%s/@@migrate-types" % self.portal_url)
        self.assertTrue(u"Migrate content-types" in self.browser.contents)
        self.browser.getControl(name='form.button.Migrate').click()
        self.assertTrue("You need to fill both required fields." in self.browser.contents)

    def test_migrate_document_to_news_view(self):
        """
        """
        self.browser.open("%s/@@migrate-types" % self.portal_url)
        self.assertTrue(u"Migrate content-types" in self.browser.contents)
        self.browser.getControl(name='src_type').value = [u"Document"]
        self.browser.getControl(name='dst_type').value = [u"News Item"]
        self.browser.getControl(name='form.button.Migrate').click()
        self.assertTrue("Migration from Document to News Item: found 10 items." in self.browser.contents)
        self.assertTrue("Migration done." in self.browser.contents)

    def test_migrate_event_to_news_view(self):
        """
        """
        self.browser.open("%s/@@migrate-types" % self.portal_url)
        self.assertTrue(u"Migrate content-types" in self.browser.contents)
        self.browser.getControl(name='src_type').value = [u"Event"]
        self.browser.getControl(name='dst_type').value = [u"News Item"]
        self.browser.getControl(name='form.button.Migrate').click()
        self.assertTrue("Migration from Event to News Item: found 0 items." in self.browser.contents)
        self.assertTrue("Migration done." in self.browser.contents)

    def test_migrate_folder_to_document_view(self):
        """
        Add a document to a folder, and check that we can't migrate a folder with some contents.
        """
        #Create a content into Folder 1
        self.browser.open(self.portal_url + "/folder-1")
        self.browser.getLink('Page').click()
        self.browser.getControl(name='title').value = "My Test Document"
        self.browser.getControl(name='form.button.save').click()
        #Now try to migrate
        self.browser.open("%s/@@migrate-types" % self.portal_url)
        self.assertTrue(u"Migrate content-types" in self.browser.contents)
        self.browser.getControl(name='src_type').value = [u"Folder"]
        self.browser.getControl(name='dst_type').value = [u"Document"]
        self.browser.getControl(name='form.button.Migrate').click()
        self.assertTrue("Migration from Folder to Document: found 2 items." in self.browser.contents)
        self.assertTrue("Errors in migration process. See the log for more infos." in self.browser.contents)
