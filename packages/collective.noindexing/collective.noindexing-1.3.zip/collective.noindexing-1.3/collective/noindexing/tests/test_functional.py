import unittest2 as unittest

from Products.CMFCore.utils import getToolByName
from plone.app.testing import TEST_USER_ID
from plone.app.testing import setRoles

from collective.noindexing.testing import (
    NOINDEXING_INTEGRATION_TESTING,
    NOINDEXING_APPLIED_INTEGRATION_TESTING,
    make_test_doc,
    apply_patches, unapply_patches,
    )


class TestNormalIndexing(unittest.TestCase):

    layer = NOINDEXING_INTEGRATION_TESTING

    def _makeOne(self):
        return make_test_doc(self.layer['portal'])

    def testNormalIndexing(self):
        portal = self.layer['portal']
        setRoles(portal, TEST_USER_ID, ('Manager',))
        catalog = getToolByName(portal, 'portal_catalog')
        base_count = len(catalog.searchResults({}))
        doc = self._makeOne()
        self.assertEqual(len(catalog.searchResults({})), base_count + 1)
        doc.unindexObject()
        self.assertEqual(len(catalog.searchResults({})), base_count)


class TestNoIndexingApplied(unittest.TestCase):

    layer = NOINDEXING_APPLIED_INTEGRATION_TESTING

    def _makeOne(self):
        return make_test_doc(self.layer['portal'])

    def testNotIndexed(self):
        portal = self.layer['portal']
        setRoles(portal, TEST_USER_ID, ('Manager',))
        catalog = getToolByName(portal, 'portal_catalog')
        base_count = len(catalog.searchResults({}))
        doc = self._makeOne()
        self.assertEqual(len(catalog.searchResults({})), base_count)
        doc.indexObject()
        self.assertEqual(len(catalog.searchResults({})), base_count)
        doc.reindexObject()
        self.assertEqual(len(catalog.searchResults({})), base_count)
        doc.unindexObject()
        self.assertEqual(len(catalog.searchResults({})), base_count)

    def testUnapply(self):
        portal = self.layer['portal']
        setRoles(portal, TEST_USER_ID, ('Manager',))
        catalog = getToolByName(portal, 'portal_catalog')
        base_count = len(catalog.searchResults({}))
        doc = self._makeOne()
        self.assertEqual(len(catalog.searchResults({})), base_count)
        unapply_patches(portal)
        self.assertEqual(len(catalog.searchResults({})), base_count)
        doc.reindexObject()
        self.assertEqual(len(catalog.searchResults({})), base_count + 1)

    def testMultiApplyAndUnapply(self):
        # Test that multiple patching and unpatching works.
        portal = self.layer['portal']
        setRoles(portal, TEST_USER_ID, ('Manager',))
        catalog = getToolByName(portal, 'portal_catalog')
        base_count = len(catalog.searchResults({}))

        # One
        apply_patches(portal)
        doc = self._makeOne()
        self.assertEqual(len(catalog.searchResults({})), base_count)
        unapply_patches(portal)
        self.assertEqual(len(catalog.searchResults({})), base_count)
        doc.reindexObject()
        self.assertEqual(len(catalog.searchResults({})), base_count + 1)
        doc.unindexObject()
        self.assertEqual(len(catalog.searchResults({})), base_count)

        # Two
        apply_patches(portal)
        doc = self._makeOne()
        self.assertEqual(len(catalog.searchResults({})), base_count)
        unapply_patches(portal)
        self.assertEqual(len(catalog.searchResults({})), base_count)
        doc.reindexObject()
        self.assertEqual(len(catalog.searchResults({})), base_count + 1)
        doc.unindexObject()
        self.assertEqual(len(catalog.searchResults({})), base_count)
