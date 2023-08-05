from Products.CMFCore.utils import getToolByName
from collective.cart.core import _
from collective.cart.core.interfaces import ICartContainer
from five import grok
from z3c.form.validator import SimpleFieldValidator
from z3c.form.validator import WidgetValidatorDiscriminators
from zope.interface import Invalid


class ValidateCartIDUniqueness(SimpleFieldValidator):
    """Validate uniqueness of  next cart ID within the cart container."""

    def validate(self, value):
        super(ValidateCartIDUniqueness, self).validate(value)

        if value is not None:
            catalog = getToolByName(self.context, 'portal_catalog')
            brains = catalog({
                'id': str(value),
                'path': {
                    'query': '/'.join(self.context.getPhysicalPath()),
                    'depth': 1,
                }
            })
            if brains:
                raise Invalid(_(u'The cart ID is already in use.'))


WidgetValidatorDiscriminators(ValidateCartIDUniqueness, field=ICartContainer['next_cart_id'])

grok.global_adapter(ValidateCartIDUniqueness)
