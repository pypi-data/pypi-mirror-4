import unittest2 as unittest
from zope.component import getUtility

from rt.atmigrator.testing import ATMIGRATOR_INTEGRATION_TESTING
from rt.atmigrator.migrator import migrateContents

class TestATMigratorMigrator(unittest.TestCase):

    layer = ATMIGRATOR_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']

    def test_content_migrator(self):
        """
        try to migrate Documents into News items
        """
        output = migrateContents(self.portal, "Document", "News Item")
        self.assertEqual(output.get('counter', 0), 10)
        self.assertEqual(output.get('error', []), [])
        self.assertTrue(self.portal.portal_catalog(portal_type="Document").actual_result_count == 0)
        self.assertTrue(self.portal.portal_catalog(portal_type="News Item").actual_result_count == 15)

    def test_folder_migrator(self):
        """
        try to migrate Documents into News items
        """
        output = migrateContents(self.portal, "Folder", "Folder")
        self.assertEqual(output.get('counter', 0), 2)
        self.assertEqual(output.get('error', []), [])
        self.assertTrue(self.portal.portal_catalog(portal_type="Folder").actual_result_count == 2)

    def test_migrate_notype_to_document(self):
        """
        try to migrate Documents into News items
        """
        output = migrateContents(self.portal, "Event", "Document")
        self.assertEqual(output.get('counter', 0), 0)
        self.assertEqual(output.get('error', []), [])
        self.assertTrue(self.portal.portal_catalog(portal_type="Document").actual_result_count == 10)
        self.assertTrue(self.portal.portal_catalog(portal_type="Event").actual_result_count == 0)

    def test_migrate_folder_to_document(self):
        """
        Try to migrate Folders into Documents.
        If the folder have elements, this can't be done.
        """
        folder = self.portal['folder-1']
        folder.invokeFactory('Document',
                             'my-page-test',
                             title="My page test",
                             text='spam spam')
        output = migrateContents(self.portal, "Folder", "Document")
        self.assertEqual(output.get('counter', 0), 2)
        self.assertNotEqual(output.get('error', []), [])
        self.assertEqual(output['error'][0]['msg'], 'Failed migration for object /plone/folder-1 (Folder -> Document)')
        self.assertTrue(self.portal.portal_catalog(portal_type="Document").actual_result_count == 12)
        self.assertTrue(self.portal.portal_catalog(portal_type="Folder").actual_result_count == 1)
        self.assertEqual(self.portal['folder-2'].portal_type, "Document")
        self.assertEqual(self.portal['folder-1'].portal_type, "Folder")

    def test_migrate_empty_folder_to_document(self):
        """
        Try to migrate Folders into Documents.
        If the folder is empty, this can be done.
        """
        output = migrateContents(self.portal, "Folder", "Document")
        self.assertEqual(output.get('counter', 0), 2)
        self.assertEqual(output.get('error', []), [])
        self.assertTrue(self.portal.portal_catalog(portal_type="Document").actual_result_count == 12)
        self.assertTrue(self.portal.portal_catalog(portal_type="Folder").actual_result_count == 0)

    def test_migrate_document_to_folder(self):
        """
        Try to migrate Documente into Folders
        """
        output = migrateContents(self.portal, "Document", "Folder")
        self.assertEqual(output.get('counter', 0), 10)
        self.assertEqual(output.get('error', []), [])
        self.assertTrue(self.portal.portal_catalog(portal_type="Document").actual_result_count == 0)
        self.assertTrue(self.portal.portal_catalog(portal_type="Folder").actual_result_count == 12)
        folder_titles = ['Folder 1', 'Folder 2', 'My page 0', 'My page 1', 'My page 2', 'My page 3', 'My page 4', 'My page 5', 'My page 6', 'My page 7', 'My page 8', 'My page 9']
        self.assertEqual([x.Title for x in self.portal.portal_catalog(portal_type="Folder", sort_on="sortable_title")], folder_titles)
