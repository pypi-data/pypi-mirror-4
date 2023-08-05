# -*- coding: utf-8 -*-
from collective.behavior.sku.tests.base import IntegrationTestCase
from zope.lifecycleevent import modified


class TestSKU(IntegrationTestCase):

    def setUp(self):
        self.portal = self.layer['portal']

    def test_subclass(self):
        from collective.behavior.sku.behavior import SKU
        self.assertTrue(issubclass(SKU, object))

    def create_folder(self):
        from plone.dexterity.utils import createContentInContainer
        folder = createContentInContainer(
            self.portal, 'collective.behavior.sku.Folder', id='folder',
            checkConstraints=False, title='Földer', description='Description of Földer.')
        modified(folder)
        return folder

    def create_instance(self):
        from collective.behavior.sku.interfaces import ISKU
        folder = self.create_folder()
        return ISKU(folder)

    def test_instance(self):
        instance = self.create_instance()
        from collective.behavior.sku.behavior import SKU
        self.assertIsInstance(instance, SKU)

    def test_instance_provides_ISKU(self):
        instance = self.create_instance()
        from collective.behavior.sku.interfaces import ISKU
        self.assertTrue(ISKU.providedBy(instance))

    def test_instance__verifyObject(self):
        instance = self.create_instance()
        from collective.behavior.sku.interfaces import ISKU
        from zope.interface.verify import verifyObject
        self.assertTrue(verifyObject(ISKU, instance))

    def test_instance__sku(self):
        """First time access to sku"""
        instance = self.create_instance()
        self.assertEqual(instance.sku, u'')

    def test_instance__context(self):
        from plone.dexterity.content import Container
        instance = self.create_instance()
        self.assertIsInstance(instance.context, Container)

    def test_instance__sku__set(self):
        instance = self.create_instance()
        instance.sku = u'SKU'
        self.assertEqual(instance.sku, u'SKU')

    def test_instance__sku__set_again(self):
        instance = self.create_instance()
        instance.sku = u'SKU'
        instance.sku = u'SKU'
        self.assertEqual(instance.sku, u'SKU')

    def test_instance__sku__set__non_unicode(self):
        instance = self.create_instance()
        with self.assertRaises(ValueError):
            instance.sku = 'SKU'
