import unittest


class TestISKU(unittest.TestCase):

    def test_subclass(self):
        from collective.behavior.sku.interfaces import ISKU
        from zope.interface import Interface
        self.assertTrue(issubclass(ISKU, Interface))

    def get_schema(self, name):
        """Get schema by name.

        :param name: Name of schema.
        :type name: str
        """
        from collective.behavior.sku.interfaces import ISKU
        return ISKU.get(name)

    def test_sku__instance(self):
        schema = self.get_schema('sku')
        from zope.schema import TextLine
        self.assertIsInstance(schema, TextLine)

    def test_sku__title(self):
        schema = self.get_schema('sku')
        self.assertEqual(schema.title, u'SKU')

    def test_sku__description(self):
        schema = self.get_schema('sku')
        self.assertEqual(
            schema.description, u'Unique ID for Stock Keeping Unit.')
