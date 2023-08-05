from Products.CMFCore.utils import getToolByName
from collective.behavior.sku.tests.base import IntegrationTestCase


class TestSetup(IntegrationTestCase):

    def setUp(self):
        self.portal = self.layer['portal']

    def test_is_collective_behavior_sku_installed(self):
        installer = getToolByName(self.portal, 'portal_quickinstaller')
        self.failUnless(
            installer.isProductInstalled('collective.behavior.sku'))

    def test_catalog__index__sku__instance(self):
        from Products.PluginIndexes.FieldIndex.FieldIndex import FieldIndex
        catalog = getToolByName(self.portal, 'portal_catalog')
        self.assertIsInstance(catalog.Indexes['sku'], FieldIndex)

    def test_catalog__index__sku__indexed_attrs(self):
        catalog = getToolByName(self.portal, 'portal_catalog')
        self.assertEqual(catalog.Indexes['sku'].indexed_attrs, ['sku'])

    def test_catalog__column__sku(self):
        catalog = getToolByName(self.portal, 'portal_catalog')
        self.assertIn('sku', catalog.schema())

    def test_metadata__version(self):
        setup = getToolByName(self.portal, 'portal_setup')
        self.assertEqual(
            setup.getVersionForProfile(
                'profile-collective.behavior.sku:default'), u'0')

    def test_uninstall__package(self):
        installer = getToolByName(self.portal, 'portal_quickinstaller')
        installer.uninstallProducts(['collective.behavior.sku'])
        self.failIf(installer.isProductInstalled('collective.behavior.sku'))
