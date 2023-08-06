from collective.cart.core.browser.template import BaseView

import unittest


class BaseViewTestCase(unittest.TestCase):
    """TestCase for BaseView"""

    def test_templatedir(self):
        from collective.cart.core.browser import template
        self.assertEqual(getattr(template, 'grokcore.view.directive.templatedir'), 'templates')

    def test_subclass(self):
        from five.grok import View
        self.assertTrue(issubclass(BaseView, View))

    def test_baseclass(self):
        self.assertTrue(getattr(BaseView, 'martian.martiandirective.baseclass'))

    def test_context(self):
        from collective.cart.core.interfaces import IShoppingSiteRoot
        self.assertEqual(getattr(BaseView, 'grokcore.component.directive.context'), IShoppingSiteRoot)

    def test_layer(self):
        from collective.cart.core.browser.interfaces import ICollectiveCartCoreLayer
        self.assertEqual(getattr(BaseView, 'grokcore.view.directive.layer'), ICollectiveCartCoreLayer)

    def test_require(self):
        self.assertEqual(getattr(BaseView, 'grokcore.security.directive.require'), ['zope2.View'])
