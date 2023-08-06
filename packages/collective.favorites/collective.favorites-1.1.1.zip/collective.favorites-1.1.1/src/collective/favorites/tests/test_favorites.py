import unittest2 as unittest

from DateTime import DateTime

from Products.CMFCore.utils import getToolByName

from collective.favorites.testing import\
    COLLECTIVE_FAVORITES_INTEGRATION_TESTING

from collective.favorites.interfaces import IFavoriteStorage
from plone.app.testing.helpers import login
from plone.app.testing.interfaces import SITE_OWNER_NAME, TEST_USER_NAME,\
    TEST_USER_ID

class TestExample(unittest.TestCase):

    layer = COLLECTIVE_FAVORITES_INTEGRATION_TESTING

    def setUp(self):
        self.app = self.layer['app']
        self.portal = self.layer['portal']
        self.qi_tool = getToolByName(self.portal, 'portal_quickinstaller')
        login(self.app, SITE_OWNER_NAME)
        self.portal.invokeFactory('Document', 'doc')
        self.portal.invokeFactory('Document', 'doc2')

    def test_product_is_installed(self):
        """ Validate that our products GS profile has been run and the product
            installed
        """
        pid = 'collective.favorites'
        installed = [p['id'] for p in self.qi_tool.listInstalledProducts()]
        self.assertTrue(pid in installed,
                        'package appears not to have been installed')

    def test_favorite_storage(self):
        storage = IFavoriteStorage(self.portal)

        # add favorite
        storage.add_favorite('toto', self.portal.doc.UID(), 'uid', date=DateTime())
        storage.add_favorite('toto', self.portal.doc2.UID(), 'uid', date=DateTime())
        self.assertEqual(len(storage.get_favorites()), 1)
        self.assertEqual(len(storage.get_favorites()['toto']), 2)

        # not two times favorite
        storage.add_favorite('toto', self.portal.doc2.UID(), 'uid', date=DateTime())
        self.assertEqual(len(storage.get_favorites()['toto']), 2)

        # remove favorite
        storage.remove_favorite('toto', self.portal.doc2.UID())
        self.assertEqual(len(storage.get_favorites()), 1)
        storage.remove_favorite('toto', self.portal.doc.UID())
        self.assertEqual(len(storage.get_favorites()), 0)

    def test_favorite_actions(self):
        login(self.portal, TEST_USER_NAME)
        self.portal.doc.restrictedTraverse('@@add-favorite')()
        storage = IFavoriteStorage(self.portal)
        self.assertEqual(len(storage.get_favorites()), 1)
        self.assertEqual(len(storage.list_favorites(TEST_USER_ID)), 1)
        self.assertEqual(len(storage.list_favorites('toto')), 0)

        self.portal.doc.restrictedTraverse('@@remove-favorite')()
        self.assertEqual(len(storage.list_favorites(TEST_USER_ID)), 0)
        self.assertEqual(len(storage.get_favorites()), 0)