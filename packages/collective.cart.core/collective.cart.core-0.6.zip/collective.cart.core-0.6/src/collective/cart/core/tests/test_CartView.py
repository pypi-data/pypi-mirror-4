from collective.cart.core.tests.base import IntegrationTestCase
from zope.publisher.browser import TestRequest


class TestCartView(IntegrationTestCase):

    def setUp(self):
        self.portal = self.layer['portal']

    def test_subclass(self):
        from collective.cart.core.browser.template import BaseCheckOutView
        from collective.cart.core.browser.template import CartView
        self.assertTrue(issubclass(CartView, BaseCheckOutView))

    def create_view(self):
        from collective.cart.core.browser.template import CartView
        request = TestRequest()
        return CartView(self.portal, request)

    def test_instance__name(self):
        instance = self.create_view()
        self.assertEqual(getattr(instance, 'grokcore.component.directive.name'), 'cart')

    def test_instance__template(self):
        instance = self.create_view()
        self.assertEqual(getattr(instance, 'grokcore.view.directive.template'), 'cart')
