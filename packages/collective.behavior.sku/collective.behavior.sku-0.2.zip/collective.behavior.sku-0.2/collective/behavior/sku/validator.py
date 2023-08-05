from Products.CMFCore.utils import getToolByName
from collective.behavior.sku import _
from collective.behavior.sku.interfaces import ISKU
from five import grok
from z3c.form.validator import SimpleFieldValidator
from z3c.form.validator import WidgetValidatorDiscriminators
from zope.interface import Invalid


class ValidateSKUUniqueness(SimpleFieldValidator):
    """Validate uniqueness of SKU."""

    def validate(self, value):
        super(ValidateSKUUniqueness, self).validate(value)
        if getattr(self.context, 'sku', u'') != value:
            catalog = getToolByName(self.context, 'portal_catalog')
            brains = catalog({
                'sku': value,
            })
            if brains:
                raise Invalid(_(u'The SKU is already in use.'))


WidgetValidatorDiscriminators(ValidateSKUUniqueness, field=ISKU['sku'])


grok.global_adapter(ValidateSKUUniqueness)
