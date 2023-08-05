from collective.behavior.sku import _
from plone.directives import form
from zope import schema


class ISKU(form.Schema):
    """Interface for SKU behavior."""

    sku = schema.TextLine(
        title=_(u"SKU"),
        description=_(u"Unique ID for Stock Keeping Unit."))
