from collective.cart.core.tests.base import IntegrationTestCase


class TestSetup(IntegrationTestCase):

    def setUp(self):
        self.portal = self.layer['portal']

    def test_subclass(self):
        from collective.base.adapter import Adapter
        from collective.cart.core.adapter.cartcontainer import CartContainerAdapter
        self.assertTrue(issubclass(CartContainerAdapter, Adapter))
        from collective.base.interfaces import IAdapter
        from collective.cart.core.interfaces import ICartContainerAdapter
        self.assertTrue(issubclass(ICartContainerAdapter, IAdapter))

    def test_context(self):
        from collective.cart.core.adapter.cartcontainer import CartContainerAdapter
        from collective.cart.core.interfaces import ICartContainer
        self.assertEqual(getattr(CartContainerAdapter, 'grokcore.component.directive.context'), ICartContainer)

    def test_provides(self):
        from collective.cart.core.adapter.cartcontainer import CartContainerAdapter
        from collective.cart.core.interfaces import ICartContainerAdapter
        self.assertEqual(getattr(CartContainerAdapter, 'grokcore.component.directive.provides'), ICartContainerAdapter)

    def create_cart_container(self):
        from plone.dexterity.utils import createContentInContainer
        from zope.lifecycleevent import modified
        container = createContentInContainer(self.portal, 'collective.cart.core.CartContainer',
            id="cart-container", title="Cart Container", checkConstraints=False)
        modified(container)
        return container

    def test_instance(self):
        from collective.cart.core.adapter.cartcontainer import CartContainerAdapter
        from collective.cart.core.interfaces import ICartContainerAdapter
        container = self.create_cart_container()
        self.assertIsInstance(ICartContainerAdapter(container), CartContainerAdapter)

    def test_instance__context(self):
        from collective.cart.core.interfaces import ICartContainer
        from collective.cart.core.interfaces import ICartContainerAdapter
        container = self.create_cart_container()
        self.assertEqual(getattr(ICartContainerAdapter(container), 'grokcore.component.directive.context'), ICartContainer)

    def test_instance__provides(self):
        from collective.cart.core.interfaces import ICartContainerAdapter
        container = self.create_cart_container()
        self.assertEqual(getattr(ICartContainerAdapter(container), 'grokcore.component.directive.provides'), ICartContainerAdapter)

    def test_update_next_cart_id(self):
        """Updating next_cart_id set one number added to the current next_cart_id."""
        container = self.create_cart_container()
        from collective.cart.core.interfaces import ICartContainerAdapter
        ICartContainerAdapter(container).update_next_cart_id()
        self.assertEqual(container.next_cart_id, 1)

        # Add cart with ID: 1
        from plone.dexterity.utils import createContentInContainer
        createContentInContainer(
            container, 'collective.cart.core.Cart', id="1", checkConstraints=False)
        ICartContainerAdapter(container).update_next_cart_id()
        self.assertEqual(container.next_cart_id, 2)

        # Add carts with ID: 2 and 3
        createContentInContainer(
            container, 'collective.cart.core.Cart', id="2", checkConstraints=False)
        createContentInContainer(
            container, 'collective.cart.core.Cart', id="3", checkConstraints=False)
        ICartContainerAdapter(container).update_next_cart_id()
        self.assertEqual(container.next_cart_id, 4)
