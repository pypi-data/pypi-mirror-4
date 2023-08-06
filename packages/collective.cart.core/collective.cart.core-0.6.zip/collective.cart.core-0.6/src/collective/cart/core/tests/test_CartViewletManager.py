import unittest


class TestCartViewletManager(unittest.TestCase):

    def test_subclass(self):
        from collective.cart.core.browser.viewlet import CartViewletManager
        from five.grok import ViewletManager
        from plone.app.viewletmanager.manager import OrderedViewletManager
        self.assertTrue(issubclass(CartViewletManager, (OrderedViewletManager, ViewletManager)))

    def test_context(self):
        from collective.cart.core.browser.viewlet import CartViewletManager
        from collective.cart.core.interfaces import IShoppingSiteRoot
        self.assertEqual(getattr(CartViewletManager, 'grokcore.component.directive.context'), IShoppingSiteRoot)

    def test_instance__layer(self):
        from collective.cart.core.browser.interfaces import ICollectiveCartCoreLayer
        from collective.cart.core.browser.viewlet import CartViewletManager
        self.assertEqual(getattr(CartViewletManager, 'grokcore.view.directive.layer'), ICollectiveCartCoreLayer)

    def test_instance__name(self):
        from collective.cart.core.browser.viewlet import CartViewletManager
        self.assertEqual(getattr(CartViewletManager, 'grokcore.component.directive.name'),
            'collective.cart.core.cartviewletmanager')
