from collective.cart.core.tests.base import IntegrationTestCase
from zope.publisher.browser import TestRequest


class TestCartContainerView(IntegrationTestCase):

    def setUp(self):
        self.portal = self.layer['portal']

    def test_subclass(self):
        from collective.cart.core.browser.template import OrdersView
        from collective.cart.core.browser.template import CartContainerView
        self.assertTrue(issubclass(CartContainerView, OrdersView))

    def create_view(self):
        from collective.cart.core.browser.template import CartContainerView
        request = TestRequest()
        return CartContainerView(self.portal, request)

    def test_instance__context(self):
        from collective.cart.core.interfaces import ICartContainer
        instance = self.create_view()
        self.assertEqual(getattr(instance, 'grokcore.component.directive.context'), ICartContainer)

    def test_instance__name(self):
        instance = self.create_view()
        self.assertEqual(getattr(instance, 'grokcore.component.directive.name'), 'view')
