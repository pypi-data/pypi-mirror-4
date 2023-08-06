from collective.cart.core.tests.base import IntegrationTestCase
from zope.publisher.browser import TestRequest


class TestCartContentView(IntegrationTestCase):

    def setUp(self):
        self.portal = self.layer['portal']

    def test_subclass(self):
        from collective.cart.core.browser.template import BaseView
        from collective.cart.core.browser.template import CartContentView
        self.assertTrue(issubclass(CartContentView, BaseView))

    def create_view(self):
        from collective.cart.core.browser.template import CartContentView
        request = TestRequest()
        return CartContentView(self.portal, request)

    def test_instance__context(self):
        from collective.cart.core.interfaces import ICart
        instance = self.create_view()
        self.assertEqual(getattr(instance, 'grokcore.component.directive.context'), ICart)

    def test_instance__name(self):
        instance = self.create_view()
        self.assertEqual(getattr(instance, 'grokcore.component.directive.name'), 'view')

    def test_instance__require(self):
        instance = self.create_view()
        self.assertEqual(getattr(instance, 'grokcore.security.directive.require'), ['collective.cart.core.ViewCartContent'])

    def test_instance__template(self):
        instance = self.create_view()
        self.assertEqual(getattr(instance, 'grokcore.view.directive.template'), 'cart-content')
